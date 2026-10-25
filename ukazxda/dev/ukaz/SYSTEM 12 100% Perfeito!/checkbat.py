import os
import time
import json
import subprocess
from datetime import datetime

DIRETORIO_DADOS = "/sdcard/servidor/dados"
ARQUIVO_LOG = os.path.join(DIRETORIO_DADOS, "camlog.txt")
ARQUIVO_FALA = os.path.join(DIRETORIO_DADOS, "fala_bat.json")
ARQUIVO_FILA = os.path.join(DIRETORIO_DADOS, "fila_audio.txt")

def obter_dados_bateria():
    try:
        with open("/sys/class/power_supply/battery/capacity", "r") as f:
            pct = int(f.read().strip())
        with open("/sys/class/power_supply/battery/status", "r") as f:
            st = f.read().strip().upper()
        descarregando = (st not in ["CHARGING", "FULL"])
        return pct, descarregando
    except Exception:
        return 100, False

def fala_esta_permitida():
    try:
        if os.path.exists(ARQUIVO_FALA):
            with open(ARQUIVO_FALA, "r", encoding="utf-8") as f:
                return json.load(f).get("enabled", True)
    except Exception:
        pass
    return True

def registrar_log(mensagem):
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linha = f"{mensagem} ({data_hora})"
    try:
        with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
    except Exception: pass
    print(linha)

def enfileirar_fala(msg):
    try:
        with open(ARQUIVO_FILA, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception: pass

def controle_carregamento(pct):
    if pct >= 50:
        cmd = "su -c 'echo 1 > /sys/class/power_supply/battery/store_mode 2>/dev/null; echo 1 > /sys/class/power_supply/battery/batt_slate_mode 2>/dev/null; echo 0 > /sys/class/power_supply/battery/charging_enabled 2>/dev/null'"
        subprocess.run(cmd, shell=True)
    elif pct <= 40:
        cmd = "su -c 'echo 0 > /sys/class/power_supply/battery/store_mode 2>/dev/null; echo 0 > /sys/class/power_supply/battery/batt_slate_mode 2>/dev/null; echo 1 > /sys/class/power_supply/battery/charging_enabled 2>/dev/null'"
        subprocess.run(cmd, shell=True)

def monitorar():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("========================================")
    print("= MONITOR BATERIA (INTEGRADO AO CHECKFALA) =")
    print("========================================")
    
    alerta_em_andamento = False

    while True:
        pct, descarregando = obter_dados_bateria()
        controle_carregamento(pct)

        if pct <= 10 and descarregando:
            registrar_log("🚨 EMERGÊNCIA BATERIA (10%): Repetindo aviso 5x e desligando celular...")
            for i in range(5):
                enfileirar_fala("Atenção! Bateria em estado crítico. Desligando o sistema agora.")
            time.sleep(35) 
            subprocess.run("su -c 'reboot -p' || su -c poweroff", shell=True)
            break

        if pct <= 38 and descarregando:
            if not alerta_em_andamento:
                registrar_log(f"⚠️ ALERTA ENERGIA: Bateria em {pct}%! Verifique o cabo.")
                alerta_em_andamento = True

            if fala_esta_permitida():
                enfileirar_fala(f"Atenção! Bateria em {pct} por cento. Verifique o cabo.")

            tempo_espera = 15
        else:
            alerta_em_andamento = False
            tempo_espera = 15

        time.sleep(tempo_espera)

if __name__ == "__main__":
    monitorar()