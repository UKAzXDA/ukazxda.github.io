import os
import subprocess
import time
import threading
import shutil
import glob
import json
import urllib.parse
import sys
from datetime import datetime

CAMINHO_SENHA_SEGURA = "/data/data/com.termux/files/home/.senha_cftv"

def obter_senha():
    if not os.path.exists(CAMINHO_SENHA_SEGURA):
        sys.exit(1)
    try:
        with open(CAMINHO_SENHA_SEGURA, "r", encoding="utf-8") as f:
            senha = f.read().strip()
        if not senha:
            sys.exit(1)
        return senha
    except Exception:
        sys.exit(1)

SENHA_CAM = obter_senha()
SENHA_URL = urllib.parse.quote(SENHA_CAM, safe='')

IP_CAMERA = "192.168.1.7"
RTSP_URL = f"rtsp://admin:{SENHA_URL}@{IP_CAMERA}:554/cam/realmonitor?channel=1&subtype=1"
DIRETORIO_DADOS = "/sdcard/servidor/dados"
DIRETORIO_VIDEOS = os.path.join(DIRETORIO_DADOS, "videos")
ARQUIVO_LOG = os.path.join(DIRETORIO_DADOS, "camlog.txt")
ARQUIVO_STATUS = os.path.join(DIRETORIO_DADOS, "status.json")
ARQUIVO_FALA = os.path.join(DIRETORIO_DADOS, "fala_cam.json")
ARQUIVO_FILA = os.path.join(DIRETORIO_DADOS, "fila_audio.txt")
ARQUIVO_CONFIG = os.path.join(DIRETORIO_DADOS, "config.json")

ESPACO_LIVRE_MINIMO_GB = 5.0
os.makedirs(DIRETORIO_VIDEOS, exist_ok=True)

class SistemaCFTV:
    def __init__(self):
        self.processo_ffmpeg = None
        self.rodando = True
        self.conectado = False
        self.ultimo_tamanho_arquivo = -1
        self.tempo_sem_crescimento = 0
        self.alarme_ativo = False

    def obter_segmento_tempo(self):
        try:
            if os.path.exists(ARQUIVO_CONFIG):
                with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                    tempo = json.load(f).get("segment_time", 900)
                    return str(tempo)
        except Exception:
            pass
        return "900"

    def enfileirar_fala(self, msg):
        try:
            with open(ARQUIVO_FILA, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except:
            pass

    def atualizar_status_site(self, status, mensagem):
        dados = {"status": status, "msg": mensagem, "hora": datetime.now().strftime('%H:%M:%S')}
        try:
            with open(ARQUIVO_STATUS, "w") as f:
                json.dump(dados, f)
        except: pass

    def registrar_log(self, mensagem, online=False):
        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        linha = f"{mensagem} ({data_hora})"
        with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
            
        os.system('clear' if os.name == 'posix' else 'cls')
        print("===========================")
        print("= SISTEMA CFTV LOCAL v9.8 =")
        print("===========================")
        print(f"\n{linha}\n")
        
        status_txt = "ONLINE" if online else "OFFLINE"
        if "Conectando" in mensagem:
            status_txt = "CONECTANDO"
        self.atualizar_status_site(status_txt, mensagem)

    def alerta_offline_continuo(self):
        while self.rodando:
            if self.alarme_ativo:
                for _ in range(15):
                    time.sleep(1)
                    if not self.alarme_ativo:
                        break
                
                if self.alarme_ativo:
                    permitido = True
                    try:
                        if os.path.exists(ARQUIVO_FALA):
                            with open(ARQUIVO_FALA, "r", encoding="utf-8") as f:
                                permitido = json.load(f).get("enabled", True)
                    except Exception: pass
                    
                    if permitido:
                        self.enfileirar_fala("Câmera offline.")
                        for _ in range(15):
                            time.sleep(1)
                            if not self.alarme_ativo:
                                break
            else:
                time.sleep(2)

    def gerenciador_armazenamento(self):
        limite_bytes = ESPACO_LIVRE_MINIMO_GB * (1024 ** 3)
        while self.rodando:
            try:
                total, usado, livre = shutil.disk_usage(DIRETORIO_VIDEOS)
                if livre < limite_bytes:
                    arquivos = glob.glob(os.path.join(DIRETORIO_VIDEOS, "*.mp4"))
                    if arquivos:
                        arquivo_mais_antigo = min(arquivos, key=os.path.getmtime)
                        os.remove(arquivo_mais_antigo)
            except Exception: pass
            time.sleep(300)

    def monitor_seguranca_fluxo(self):
        while self.rodando:
            time.sleep(5)
            try:
                if self.processo_ffmpeg and self.processo_ffmpeg.poll() is None:
                    arquivos = glob.glob(os.path.join(DIRETORIO_VIDEOS, "*.mp4"))
                    if arquivos:
                        arquivo_recente = max(arquivos, key=os.path.getmtime)
                        tamanho_atual = os.path.getsize(arquivo_recente)

                        if tamanho_atual > 0:
                            if not self.conectado:
                                self.conectado = True
                                self.alarme_ativo = False
                                self.registrar_log("✅ Câmera ONLINE e gravando", online=True)

                            if tamanho_atual == self.ultimo_tamanho_arquivo:
                                self.tempo_sem_crescimento += 5
                            else:
                                self.tempo_sem_crescimento = 0
                                self.ultimo_tamanho_arquivo = tamanho_atual

                            if self.tempo_sem_crescimento >= 30:
                                self.registrar_log("🚨 ALERTA: Sinal da câmera travado/perdido! Reiniciando...", online=False)
                                self.conectado = False
                                self.alarme_ativo = True
                                self.processo_ffmpeg.kill()
                                self.tempo_sem_crescimento = 0
            except Exception: pass

    def iniciar_captura(self):
        self.ultimo_tamanho_arquivo = -1
        self.tempo_sem_crescimento = 0
        caminho_output = os.path.join(DIRETORIO_VIDEOS, "%Y-%m-%d_%H-%M-%S.mp4")
        segment_time = self.obter_segmento_tempo()

        comando = [
            "ffmpeg", "-y",
            "-fflags", "+genpts",
            "-hide_banner", "-loglevel", "error",
            "-rtsp_transport", "tcp",
            "-i", RTSP_URL,
            "-c:v", "copy",
            "-c:a", "aac",
            "-f", "segment",
            "-segment_time", segment_time,
            "-segment_format", "mp4",
            "-segment_format_options", "movflags=frag_keyframe+empty_moov+default_base_moof",
            "-reset_timestamps", "1",
            "-strftime", "1",
            caminho_output
        ]

        self.registrar_log("⏳ Conectando à câmera...", online=False)
        self.processo_ffmpeg = subprocess.Popen(comando)
        self.processo_ffmpeg.wait()

        if self.conectado:
            self.conectado = False
            self.registrar_log("🚨 Câmera OFFLINE / Queda de Sinal", online=False)
            self.alarme_ativo = True
        else:
            self.registrar_log("❌ Falha na conexão ou Timeout. Tentando novamente...", online=False)
            self.alarme_ativo = True

        time.sleep(3)

    def executar(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self.atualizar_status_site("INICIANDO", "Sistema inicializando...")
        
        threading.Thread(target=self.gerenciador_armazenamento, daemon=True).start()
        threading.Thread(target=self.monitor_seguranca_fluxo, daemon=True).start()
        threading.Thread(target=self.alerta_offline_continuo, daemon=True).start()
        
        try:
            while self.rodando:
                self.iniciar_captura()
        except KeyboardInterrupt:
            self.rodando = False
            if self.processo_ffmpeg:
                self.processo_ffmpeg.terminate()
            self.registrar_log("= Sistema encerrado pelo usuário.", online=False)

if __name__ == "__main__":
    cftv = SistemaCFTV()
    cftv.executar()