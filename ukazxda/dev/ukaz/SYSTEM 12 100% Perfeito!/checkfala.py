import os
import time
import subprocess
import fcntl

ARQUIVO_FILA = "/sdcard/servidor/dados/fila_audio.txt"
ARQUIVO_WAV = "/sdcard/servidor/dados/temp_audio.wav"

os.makedirs("/sdcard/servidor/dados", exist_ok=True)

def tocar_audio():
    if not os.path.exists(ARQUIVO_FILA): return
    
    try:
        with open(ARQUIVO_FILA, "r+", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            linhas = f.readlines()
            
            if not linhas:
                fcntl.flock(f, fcntl.LOCK_UN)
                return
                
            msg = linhas[0].strip()
            f.seek(0)
            f.writelines(linhas[1:])
            f.truncate()
            fcntl.flock(f, fcntl.LOCK_UN)

        if msg:
            print(f"[ÁUDIO] Falando: {msg}")
            subprocess.run("termux-volume music 15", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(f'espeak-ng -v pt-br "{msg}" -w {ARQUIVO_WAV}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(f'termux-media-player play {ARQUIVO_WAV}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            while True:
                try:
                    status = subprocess.check_output("termux-media-player info", shell=True, stderr=subprocess.DEVNULL).decode('utf-8')
                    if "Playing" not in status: break
                except Exception:
                    break
                time.sleep(1)
            time.sleep(1) 
    except Exception as e:
        pass

print("=== GERENCIADOR DE FALA (checkfala.py) ATIVO ===")
while True:
    tocar_audio()
    time.sleep(1)