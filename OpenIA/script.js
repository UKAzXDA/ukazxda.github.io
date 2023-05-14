// Seleciona os elementos HTML relevantes
const timerEl = document.querySelector('.timer');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const reasonInput = document.getElementById('reason');
const reportTable = document.getElementById('report').getElementsByTagName('tbody')[0];

let intervalId; // Variável para armazenar o ID do intervalo

// Converte um número de segundos para uma string formatada como 'HH:MM:SS'
function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor(seconds / 60) % 60;
  const secs = seconds % 60;
  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Atualiza o elemento do temporizador com o tempo decorrido
function updateTimer(startTime) {
  const elapsedSecs = Math.floor((Date.now() - startTime) / 1000);
  timerEl.textContent = formatTime(elapsedSecs);
}

// Cria uma nova linha na tabela de relatórios com os dados fornecidos
function addReportEntry(reason, startTime, endTime) {
  const totalMins = Math.floor((endTime - startTime) / 1000 / 60);
  const newRow = reportTable.insertRow(-1);
  const reasonCell = newRow.insertCell(0);
  const startTimeCell = newRow.insertCell(1);
  const endTimeCell = newRow.insertCell(2);
  const totalMinsCell = newRow.insertCell(3);
  reasonCell.textContent = reason;
  startTimeCell.textContent = new Date(startTime).toLocaleTimeString();
  endTimeCell.textContent = new Date(endTime).toLocaleTimeString();
  totalMinsCell.textContent = totalMins;
}

// Inicia a contagem regressiva e atualiza o temporizador a cada segundo
function startTimer() {
  const reason = reasonInput.value;
  const startTime = Date.now();
  updateTimer(startTime);
  intervalId = setInterval(() => {
    updateTimer(startTime);
  }, 1000);
  startBtn.disabled = true;
  reasonInput.disabled = true;
  stopBtn.disabled = false;
}

// Pausa a contagem regressiva e adiciona uma entrada à tabela de relatórios
function stopTimer() {
  clearInterval(intervalId);
  const reason = reasonInput.value;
  const startTime = Date.now() - (Number(timerEl.textContent.split(':')[0]) * 60 * 1000) - (Number(timerEl.textContent.split(':')[1]) * 1000);
  const endTime = Date.now();
  addReportEntry(reason, startTime, endTime);
  timerEl.textContent = '00:00';
  startBtn.disabled = false;
  reasonInput.disabled = false;
  stopBtn.disabled = true;
  reasonInput.value = '';
}

// Associa os manipuladores de eventos aos botões relevantes
startBtn.addEventListener('click', startTimer);
stopBtn.addEventListener('click', stopTimer);
