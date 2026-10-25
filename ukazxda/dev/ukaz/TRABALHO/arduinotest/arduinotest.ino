/*
 * ============================================================================
 * SISTEMA DE PULTRUSÃO DE FILAMENTO RECICLADO (PET, HDPE, PP, ABS)
 * Hardware: Arduino Mega 2560 + RAMPS 1.4 + Driver DRV8825 + Extrusora MK8
 * Controle: Serial/Web (Flask) + Botões Fim de Curso (FIM -X e FIM -Z)
 * ============================================================================
 */

#include <Arduino.h>

// ============================================================================
// ⚙️ TABELA DE CONFIGURAÇÃO FIXA (AJUSTE SEUS VALORES AQUI)
// ============================================================================
const float COLD_PROTECTION_TEMP = 260.0; // Temp. mínima (°C) para o motor da extrusora girar

// Níveis de Extrusão (Adicione ou remova níveis livremente)
const float EXTRUSION_TEMPS[] = {265.0}; 
const float EXTRUSION_FREQS[] = {1000.0}; 

// Cálculo automático do total de níveis de extrusão
const int NUM_EXTRUSION_LEVELS = sizeof(EXTRUSION_TEMPS) / sizeof(EXTRUSION_TEMPS[0]);

// Níveis do Cortador (Ajuste a velocidade em Hz)
const float CUTTER_FREQS[] = {1000.0, 9000.0, 24000.0}; 
const int NUM_CUTTER_LEVELS = sizeof(CUTTER_FREQS) / sizeof(CUTTER_FREQS[0]);

// ============================================================================
// 🔌 MAPEAMENTO DE PINOS (RAMPS 1.4)
// ============================================================================
#define X_STEP_PIN     54  // Passo do Motor X (Pultrusão / Cortador)
#define X_DIR_PIN      55  // Direção do Motor X
#define X_ENABLE_PIN   38  // Enable do Driver DRV8825

#define HEATER_0_PIN   10  // MOSFET D10 (Bloco Aquecedor MK8)
#define FAN_PIN         8  // MOSFET D8 (Ventoinha de Resfriamento)
#define TEMP_0_PIN    A13  // Sensor Termistor NTC 100K (T0)

// Botões Fim de Curso RAMPS 1.4
#define X_MIN_PIN       3  // Botão FIM -X (Cortador / Níveis de Extrusão)
#define Z_MIN_PIN      18  // Botão FIM -Z (Liga/Desliga Extrusão e Aquecedor)

#define INVERT_X_DIR   false 

// --- ESTADO DO MOTOR ---
bool motorEnabled = false;
bool targetDir = false;       // false = Anti-horário (Padrão), true = Horário
float targetFreq = 0.0;       
float currentFreq = 0.0;      
unsigned long halfPeriodUs = 0;
unsigned long lastStepUs = 0;
unsigned long lastRampUs = 0;
bool stepState = false;

// --- ESTADO DA TEMPERATURA E PID ---
bool heaterEnabled = false;
float targetTemp = 0.0;
float currentTemp = 0.0;
unsigned long lastTempMs = 0;

float Kp = 24.5;
float Ki = 1.25;
float Kd = 110.0;

float iTerm = 0.0;
float lastTempForPID = 0.0;
int heaterPwm = 0;

// --- MODOS DE OPERAÇÃO E NÍVEIS ---
bool cutterActive = false;
int cutterLevel = 1;     
int extrusionLevel = 1;  

// --- ESTRUTURA PARA DETECÇÃO DE MULTI-CLIQUE NOS BOTÕES ---
struct Button {
  uint8_t pin;
  bool lastState;
  bool currentState;
  unsigned long lastDebounceTime;
  unsigned long lastPressTime;
  int clickCount;
};

Button btnX = {X_MIN_PIN, HIGH, HIGH, 0, 0, 0};
Button btnZ = {Z_MIN_PIN, HIGH, HIGH, 0, 0, 0};

// Buffer Serial Non-Blocking
char serialBuf[64];
byte serialIdx = 0;

// --- DESLIGAMENTO GERAL DE SEGURANÇA ---
void shutdownAll() {
  heaterEnabled = false;
  targetTemp = 0.0;
  motorEnabled = false;
  targetFreq = 0.0;
  cutterActive = false;
  cutterLevel = 1;
  extrusionLevel = 1;
  analogWrite(HEATER_0_PIN, 0);
  digitalWrite(FAN_PIN, LOW);
  digitalWrite(X_ENABLE_PIN, HIGH);
}

// --- CÁLCULO DE FREQUÊNCIA PROGRESSIVA BASEADA NA TEMPERATURA REAL ---
float getExtrusionFreqForTemp(float temp, int maxLevel) {
  if (temp < COLD_PROTECTION_TEMP) return 0.0; 

  int idx = constrain(maxLevel - 1, 0, NUM_EXTRUSION_LEVELS - 1);
  float targetT = EXTRUSION_TEMPS[idx];
  float maxF = EXTRUSION_FREQS[idx];

  if (temp >= targetT) return maxF;

  float ratio = (temp - COLD_PROTECTION_TEMP) / (targetT - COLD_PROTECTION_TEMP);
  ratio = constrain(ratio, 0.0, 1.0);
  return ratio * maxF;
}

// --- LEITURA DO TERMISTOR COM OVERSAMPLING ---
float readHotendTemp() {
  long rawSum = 0;
  for (int i = 0; i < 16; i++) {
    rawSum += analogRead(TEMP_0_PIN);
  }
  float raw = rawSum / 16.0;

  if (raw >= 1020.0 || raw <= 2.0) return 0.0;

  float resistance = 4700.0 * raw / (1023.0 - raw);
  float steinhart = resistance / 100000.0;
  steinhart = log(steinhart); 
  steinhart /= 3950.0; 
  steinhart += 1.0 / (25.0 + 273.15); 
  steinhart = 1.0 / steinhart; 
  return steinhart - 273.15; 
}

// --- CONTROLE PID TÉRMICO ---
void updateHeaterPID() {
  unsigned long now = millis();
  float dt = (now - lastTempMs) / 1000.0;
  if (dt < 0.1) return;
  lastTempMs = now;

  currentTemp = readHotendTemp();

  if (!heaterEnabled || targetTemp <= 0.0) {
    heaterPwm = 0;
    iTerm = 0.0;
    analogWrite(HEATER_0_PIN, 0);
    digitalWrite(FAN_PIN, LOW);
    return;
  }

  digitalWrite(FAN_PIN, HIGH);
  float error = targetTemp - currentTemp;

  if (currentTemp > 410.0) {
    shutdownAll();
    return;
  }

  if (abs(error) < 20.0) {
    iTerm += (Ki * error * dt);
    iTerm = constrain(iTerm, 0.0, 255.0);
  } else if (error >= 20.0) {
    iTerm = 0.0;
    heaterPwm = 255;
    analogWrite(HEATER_0_PIN, 255);
    return;
  } else {
    iTerm = 0.0;
    heaterPwm = 0;
    analogWrite(HEATER_0_PIN, 0);
    return;
  }

  float dInput = (currentTemp - lastTempForPID) / dt;
  lastTempForPID = currentTemp;

  float feedforward = 0.0;
  if (motorEnabled && currentFreq > 0.0) {
    feedforward = (currentFreq / 25000.0) * 22.0;
  }

  float output = (Kp * error) + iTerm - (Kd * dInput) + feedforward;
  heaterPwm = constrain((int)output, 0, 255);
  analogWrite(HEATER_0_PIN, heaterPwm);
}

// --- LÓGICA DO BOTÃO FIM -Z (LIGA/DESLIGA EXTRUSÃO E AQUECEDOR) ---
void onButtonZClick(int clicks) {
  if (clicks == 1) {
    if (heaterEnabled) {
      shutdownAll();
    } else {
      cutterActive = false;
      cutterLevel = 1;
      heaterEnabled = true;
      extrusionLevel = 1;
      targetTemp = EXTRUSION_TEMPS[0]; 
      motorEnabled = true;
    }
  }
}

// --- LÓGICA DO BOTÃO FIM -X (CORTADOR OU TROCA DE NÍVEIS) ---
void onButtonXClick(int clicks) {
  if (!heaterEnabled) {
    if (clicks == 1) {
      cutterActive = !cutterActive;
      if (cutterActive) {
        cutterLevel = 1;
        targetFreq = CUTTER_FREQS[0]; 
        motorEnabled = true;
      } else {
        motorEnabled = false;
        targetFreq = 0.0;
        cutterLevel = 1;
      }
    } else if (clicks == 2 && cutterActive) {
      cutterLevel++;
      if (cutterLevel > NUM_CUTTER_LEVELS) cutterLevel = 1;
      targetFreq = CUTTER_FREQS[cutterLevel - 1]; 
    }
  } 
  else {
    if (clicks == 2) {
      extrusionLevel++;
      if (extrusionLevel > NUM_EXTRUSION_LEVELS) extrusionLevel = 1;
      targetTemp = EXTRUSION_TEMPS[extrusionLevel - 1]; 
    }
  }
}

// --- LEITURA E DEBOUNCE DOS BOTÕES FIM DE CURSO ---
void handleButtons() {
  unsigned long now = millis();

  bool readingX = digitalRead(X_MIN_PIN);
  if (readingX != btnX.lastState) {
    btnX.lastDebounceTime = now;
    btnX.lastState = readingX;
  }
  if ((now - btnX.lastDebounceTime) > 30) {
    if (readingX != btnX.currentState) {
      btnX.currentState = readingX;
      if (btnX.currentState == LOW) {
        btnX.clickCount++;
        btnX.lastPressTime = now;
      }
    }
  }
  if (btnX.clickCount > 0 && (now - btnX.lastPressTime > 300)) {
    int clicks = btnX.clickCount;
    btnX.clickCount = 0;
    onButtonXClick(clicks);
  }

  bool readingZ = digitalRead(Z_MIN_PIN);
  if (readingZ != btnZ.lastState) {
    btnZ.lastDebounceTime = now;
    btnZ.lastState = readingZ;
  }
  if ((now - btnZ.lastDebounceTime) > 30) {
    if (readingZ != btnZ.currentState) {
      btnZ.currentState = readingZ;
      if (btnZ.currentState == LOW) {
        btnZ.clickCount++;
        btnZ.lastPressTime = now;
      }
    }
  }
  if (btnZ.clickCount > 0 && (now - btnZ.lastPressTime > 300)) {
    int clicks = btnZ.clickCount;
    btnZ.clickCount = 0;
    onButtonZClick(clicks);
  }
}

void applyDirection(bool dir) {
  bool finalDir = INVERT_X_DIR ? !dir : dir;
  digitalWrite(X_DIR_PIN, finalDir ? HIGH : LOW);
}

void parseCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  if (cmd == "GET_STATUS") {
    Serial.print("STAT:");
    Serial.print(currentTemp, 1); Serial.print(",");
    Serial.print(targetTemp, 1); Serial.print(",");
    Serial.print(heaterEnabled ? "1" : "0"); Serial.print(",");
    Serial.print(targetFreq, 0); Serial.print(",");
    Serial.print(motorEnabled ? "1" : "0"); Serial.print(",");
    Serial.print(targetDir ? "1" : "0"); Serial.print(",");
    Serial.println(digitalRead(FAN_PIN) == HIGH ? "1" : "0");
    return;
  }

  if (cmd.startsWith("SET_MOTOR:")) {
    int firstComma = cmd.indexOf(',');
    int secondComma = cmd.indexOf(',', firstComma + 1);
    if (firstComma > 0 && secondComma > firstComma) {
      motorEnabled = cmd.substring(10, firstComma).toInt() == 1;
      targetFreq = cmd.substring(firstComma + 1, secondComma).toFloat();
      targetDir = cmd.substring(secondComma + 1).toInt() == 1;
      if (targetFreq > 25000.0) targetFreq = 25000.0;
      applyDirection(targetDir);
    }
  }

  if (cmd.startsWith("SET_HEATER:")) {
    int comma = cmd.indexOf(',');
    if (comma > 0) {
      heaterEnabled = cmd.substring(11, comma).toInt() == 1;
      targetTemp = comma + 1 < cmd.length() ? cmd.substring(comma + 1).toFloat() : 0.0;
      if (targetTemp > 400.0) targetTemp = 400.0;
      if (!heaterEnabled) shutdownAll();
    }
  }
}

void checkSerialNonBlocking() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (serialIdx > 0) {
        serialBuf[serialIdx] = '\0';
        parseCommand(String(serialBuf));
        serialIdx = 0;
      }
    } else if (serialIdx < 63) {
      serialBuf[serialIdx++] = c;
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);
  digitalWrite(X_ENABLE_PIN, HIGH);

  pinMode(X_MIN_PIN, INPUT_PULLUP);
  pinMode(Z_MIN_PIN, INPUT_PULLUP);

  pinMode(HEATER_0_PIN, OUTPUT);
  analogWrite(HEATER_0_PIN, 0);

  pinMode(FAN_PIN, OUTPUT);
  digitalWrite(FAN_PIN, LOW);

  applyDirection(targetDir);
}

void loop() {
  checkSerialNonBlocking();
  handleButtons();
  updateHeaterPID();

  if (heaterEnabled) {
    targetFreq = getExtrusionFreqForTemp(currentTemp, extrusionLevel);
  }

  if (motorEnabled && targetFreq > 0.0) {
    digitalWrite(X_ENABLE_PIN, LOW);
  } else {
    digitalWrite(X_ENABLE_PIN, HIGH);
  }

  unsigned long nowUs = micros();
  if (nowUs - lastRampUs >= 800) {
    lastRampUs = nowUs;
    float effectiveTarget = (motorEnabled && targetFreq > 0.0) ? targetFreq : 0.0;

    float accelStep = 40.0;
    if (effectiveTarget > 10000.0) accelStep = 100.0;

    if (currentFreq < effectiveTarget) {
      currentFreq += accelStep;
      if (currentFreq > effectiveTarget) currentFreq = effectiveTarget;
    } else if (currentFreq > effectiveTarget) {
      currentFreq -= accelStep * 1.5;
      if (currentFreq < effectiveTarget) currentFreq = effectiveTarget;
    }

    if (currentFreq >= 10.0) {
      halfPeriodUs = (unsigned long)(500000.0 / currentFreq);
    } else {
      halfPeriodUs = 0;
    }
  }

  if (halfPeriodUs > 0) {
    if (nowUs - lastStepUs >= halfPeriodUs) {
      lastStepUs = nowUs;
      stepState = !stepState;
      digitalWrite(X_STEP_PIN, stepState);
    }
  }
}