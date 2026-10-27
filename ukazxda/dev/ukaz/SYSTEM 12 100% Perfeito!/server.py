import http.server
import socketserver
import json
import os
import subprocess
import urllib.parse
import re
import base64
import shutil
import sys
import threading
import time

PORT = 8080
DIRETORIO_DADOS = "/sdcard/servidor/dados"
DIRETORIO_THUMBS = os.path.join(DIRETORIO_DADOS, "thumbs")
ARQUIVO_CONFIG = os.path.join(DIRETORIO_DADOS, "config.json")

# === SISTEMA DE SENHA BLINDADA (FAIL-SECURE) ===
CAMINHO_SENHA_SEGURA = "/data/data/com.termux/files/home/.senha_cftv"

def obter_senha():
    if not os.path.exists(CAMINHO_SENHA_SEGURA):
        print("🚨 ERRO CRÍTICO: Arquivo de senha não encontrado no sistema!")
        print(f"Por segurança, o servidor foi bloqueado. Crie o arquivo em: {CAMINHO_SENHA_SEGURA}")
        sys.exit(1)
        
    try:
        with open(CAMINHO_SENHA_SEGURA, "r", encoding="utf-8") as f:
            senha = f.read().strip()
            
        if not senha:
            print("🚨 ERRO CRÍTICO: O arquivo de senha está vazio!")
            sys.exit(1)
            
        return senha
    except Exception as e:
        print(f"🚨 ERRO CRÍTICO: Falha ao tentar ler a senha protegida: {e}")
        sys.exit(1)

SENHA_ADM = obter_senha()
os.makedirs(DIRETORIO_DADOS, exist_ok=True)
os.makedirs(DIRETORIO_THUMBS, exist_ok=True)

def obter_status_bateria():
    try:
        out = subprocess.check_output(["termux-battery-status"], timeout=2).decode('utf-8')
        dados = json.loads(out)
        return {
            "percentage": dados.get("percentage", 0),
            "plugged": dados.get("plugged", "UNPLUGGED")
        }
    except Exception:
        try:
            with open("/sys/class/power_supply/battery/capacity", "r") as f: cap = int(f.read().strip())
            with open("/sys/class/power_supply/battery/status", "r") as f: st = f.read().strip()
            return {"percentage": cap, "plugged": "PLUGGED" if st != "Discharging" else "UNPLUGGED"}
        except:
            return {"percentage": 0, "plugged": "UNKNOWN"}

def status_fala_ativa(arquivo):
    try:
        caminho = os.path.join(DIRETORIO_DADOS, arquivo)
        if os.path.exists(caminho):
            with open(caminho, "r") as f:
                return json.load(f).get("enabled", True)
    except: pass
    return True

# === GERADOR DE THUMBNAILS JPG (ULTRA-RÁPIDO) ===
def gerar_thumbnail_video(video_nome):
    pasta_videos = os.path.join(DIRETORIO_DADOS, "videos")
    video_path = os.path.join(pasta_videos, video_nome)
    thumb_path = os.path.join(DIRETORIO_THUMBS, f"{video_nome}.jpg")

    if not os.path.exists(video_path):
        return None

    if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
        return thumb_path

    comando = [
        "ffmpeg", "-y",
        "-ss", "00:00:01",
        "-i", video_path,
        "-vframes", "1",
        "-vf", "scale=320:-1",
        "-q:v", "5",
        thumb_path
    ]
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
        return thumb_path
    return None

def atualizador_de_thumb():
    while True:
        try:
            pasta_videos = os.path.join(DIRETORIO_DADOS, "videos")
            thumb_live = os.path.join(DIRETORIO_DADOS, "live_thumb.jpg")
            
            if os.path.exists(pasta_videos):
                mp4s = [f for f in os.listdir(pasta_videos) if f.endswith('.mp4')]
                if mp4s:
                    mp4s.sort(key=lambda x: os.path.getmtime(os.path.join(pasta_videos, x)), reverse=True)
                    video_atual = os.path.join(pasta_videos, mp4s[0])
                    
                    # Live Thumb do vídeo em gravação
                    comando = [
                        "ffmpeg", "-y", 
                        "-sseof", "-2", 
                        "-i", video_atual, 
                        "-update", "1",
                        "-vframes", "1", 
                        "-vf", "scale=320:-1",
                        "-q:v", "5", 
                        thumb_live
                    ]
                    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    # Pré-gera capas de vídeos gravados em segundo plano
                    for video in mp4s[1:]:
                        thumb_file = os.path.join(DIRETORIO_THUMBS, f"{video}.jpg")
                        if not os.path.exists(thumb_file):
                            gerar_thumbnail_video(video)
                            time.sleep(0.3)
        except Exception:
            pass
        time.sleep(10)

# Servidor HTTP Multi-Threaded para resposta instantânea
class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class CFTVHandler(http.server.SimpleHTTPRequestHandler):
    def do_HEAD(self):
        super().do_HEAD()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            try:
                with open(os.path.join(DIRETORIO_DADOS, "status.json"), "r") as f:
                    status_data = json.load(f)
            except:
                status_data = {"status": "OFFLINE", "msg": "Aguardando..."}
            
            try:
                if os.path.exists(ARQUIVO_CONFIG):
                    with open(ARQUIVO_CONFIG, "r") as f:
                        status_data["segment_time"] = json.load(f).get("segment_time", 900)
                else:
                    status_data["segment_time"] = 900
            except:
                status_data["segment_time"] = 900

            status_data["bateria"] = obter_status_bateria()
            status_data["fala_cam"] = status_fala_ativa("fala_cam.json")
            status_data["fala_bat"] = status_fala_ativa("fala_bat.json")
            self.wfile.write(json.dumps(status_data).encode())
            return

        if parsed.path == "/api/thumb":
            query = urllib.parse.parse_qs(parsed.query)
            video_nome = query.get("v", [""])[0]
            if video_nome and ".." not in video_nome:
                thumb_path = gerar_thumbnail_video(video_nome)
                if thumb_path and os.path.exists(thumb_path):
                    self.send_response(200)
                    self.send_header("Content-type", "image/jpeg")
                    self.send_header("Cache-Control", "public, max-age=86400")
                    self.end_headers()
                    with open(thumb_path, "rb") as f:
                        shutil.copyfileobj(f, self.wfile)
                    return
            self.send_response(404)
            self.end_headers()
            return

        if parsed.path == "/api/videos":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            
            pasta_videos = os.path.join(DIRETORIO_DADOS, "videos")
            arquivos = []
            try:
                now = time.time()
                if os.path.exists(pasta_videos):
                    for f in os.listdir(pasta_videos):
                        if f.endswith('.mp4'):
                            caminho_completo = os.path.join(pasta_videos, f)
                            tamanho = os.path.getsize(caminho_completo)
                            mtime = os.path.getmtime(caminho_completo)
                            arquivos.append({
                                "nome": f,
                                "tamanho_bytes": tamanho,
                                "gravando": False,
                                "mtime": mtime
                            })
                    arquivos.sort(key=lambda x: x["mtime"], reverse=True)
                    if arquivos and (now - arquivos[0]["mtime"]) < 15:
                        arquivos[0]["gravando"] = True
            except Exception: pass
            
            self.wfile.write(json.dumps(arquivos).encode())
            return

        if parsed.path == "/api/logs":
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                arq_log = os.path.join(DIRETORIO_DADOS, "camlog.txt")
                if os.path.exists(arq_log):
                    with open(arq_log, "r", encoding="utf-8") as f:
                        logs = f.read()
                else: logs = "Nenhum registro de log encontrado."
            except Exception as e: logs = f"Erro: {str(e)}"
            self.wfile.write(logs.encode('utf-8'))
            return

        if parsed.path == "/api/explorer":
            query = urllib.parse.parse_qs(parsed.query)
            current_path = query.get("dir", ["."])[0]
            base_dir = "/sdcard/servidor"
            target_dir = os.path.abspath(os.path.join(base_dir, current_path))
            
            if not target_dir.startswith(base_dir):
                target_dir = base_dir
                
            items = []
            try:
                for f in os.listdir(target_dir):
                    full_path = os.path.join(target_dir, f)
                    rel_path = os.path.relpath(full_path, base_dir)
                    is_dir = os.path.isdir(full_path)
                    size = os.path.getsize(full_path) if not is_dir else 0
                    items.append({
                        "name": f,
                        "path": rel_path.replace('\\', '/'),
                        "is_dir": is_dir,
                        "size": size
                    })
                items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
            except Exception: pass
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "current_dir": os.path.relpath(target_dir, base_dir).replace('\\', '/'),
                "items": items
            }).encode('utf-8'))
            return

        if parsed.path == "/api/ler_arquivo":
            query = urllib.parse.parse_qs(parsed.query)
            rel_path = query.get("path", [""])[0]
            base_dir = "/sdcard/servidor"
            target_file = os.path.abspath(os.path.join(base_dir, rel_path))
            
            if not target_file.startswith(base_dir) or not os.path.isfile(target_file):
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Arquivo invalido"}')
                return

            try:
                with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                    conteudo = f.read()
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"conteudo": conteudo}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        filepath = self.translate_path(self.path)
        if os.path.isfile(filepath) and filepath.endswith('.mp4'):
            self.serve_video_range(filepath)
            return

        super().do_GET()

    def serve_video_range(self, filepath):
        try:
            file_size = os.path.getsize(filepath)
            range_header = self.headers.get('Range', None)

            if not range_header:
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(file_size))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                with open(filepath, 'rb') as f:
                    shutil.copyfileobj(f, self.wfile)
                return

            match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            if not match: return self.send_error(400, "Bad Range")

            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1

            if start >= file_size or end >= file_size:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{file_size}")
                self.end_headers()
                return

            length = end - start + 1
            self.send_response(206)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            with open(filepath, 'rb') as f:
                f.seek(start)
                chunk_size = 64 * 1024
                bytes_left = length
                while bytes_left > 0:
                    read_bytes = min(chunk_size, bytes_left)
                    data = f.read(read_bytes)
                    if not data: break
                    self.wfile.write(data)
                    bytes_left -= len(data)
        except Exception: pass

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try: data = json.loads(post_data)
        except: data = {}

        if data.get("senha") != SENHA_ADM:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'{"error": "Senha Incorreta!"}')
            return

        if parsed.path == "/api/teste_senha":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"success": true}')
            return

        if parsed.path == "/api/exec_cmd":
            cmd = data.get("cmd", "").strip()
            cwd = data.get("cwd", "/sdcard/servidor")
            
            if not os.path.exists(cwd):
                cwd = "/sdcard/servidor"

            if cmd.startswith("cd ") or cmd == "cd":
                target = cmd[3:].strip() if len(cmd) > 2 else "/data/data/com.termux/files/home"
                if target == "~":
                    new_dir = os.path.expanduser("~")
                elif target.startswith("~/"):
                    new_dir = os.path.expanduser(target)
                else:
                    new_dir = os.path.abspath(os.path.join(cwd, target))
                
                if os.path.exists(new_dir) and os.path.isdir(new_dir):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({"output": "", "new_cwd": new_dir, "returncode": 0}).encode('utf-8'))
                else:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({"output": f"cd: {target}: Diretório não encontrado\n", "new_cwd": cwd, "returncode": 1}).encode('utf-8'))
                return

            cmd_run = cmd
            if cmd_run == "ls" or cmd_run.startswith("ls "):
                if "--color" not in cmd_run:
                    cmd_run = re.sub(r'\bls\b', 'ls --color=always', cmd_run, count=1)

            env = os.environ.copy()
            env["TERM"] = "xterm-256color"
            env["CLICOLOR_FORCE"] = "1"
            env["FORCE_COLOR"] = "1"

            try:
                res = subprocess.run(
                    cmd_run, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    cwd=cwd, 
                    env=env,
                    timeout=30
                )
                out = res.stdout + res.stderr
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "output": out if out else "(Comando executado sem retorno visual)\n",
                    "new_cwd": cwd,
                    "returncode": res.returncode
                }).encode('utf-8'))
            except subprocess.TimeoutExpired:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"output": "⏰ Comando excedeu o tempo limite de 30 segundos.\n", "new_cwd": cwd, "returncode": 124}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        if parsed.path == "/api/salvar_arquivo":
            rel_path = data.get("path")
            conteudo = data.get("conteudo")
            if rel_path and conteudo is not None:
                base_dir = "/sdcard/servidor"
                target_file = os.path.abspath(os.path.join(base_dir, rel_path))
                
                if not target_file.startswith(base_dir):
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'{"error": "Caminho invalido"}')
                    return

                try:
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(conteudo)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"success": true}')
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
            
        if parsed.path == "/api/config_tempo":
            tempo = data.get("tempo")
            if tempo and isinstance(tempo, int):
                try:
                    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
                        json.dump({"segment_time": tempo}, f)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"success": true}')
                    subprocess.run("pkill -2 -f ffmpeg", shell=True) 
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        
        if parsed.path == "/api/formatar_dados":
            try:
                if os.path.exists(DIRETORIO_DADOS):
                    for arquivo_pasta in os.listdir(DIRETORIO_DADOS):
                        caminho_item = os.path.join(DIRETORIO_DADOS, arquivo_pasta)
                        if os.path.isfile(caminho_item) or os.path.islink(caminho_item):
                            os.unlink(caminho_item)
                        elif os.path.isdir(caminho_item):
                            shutil.rmtree(caminho_item)
                
                os.makedirs(os.path.join(DIRETORIO_DADOS, "videos"), exist_ok=True)
                os.makedirs(DIRETORIO_THUMBS, exist_ok=True)
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"success": true}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        if parsed.path == "/api/toggle_fala":
            alvo = data.get("alvo", "cam")
            novo_estado = data.get("enabled", True)
            arquivo = "fala_cam.json" if alvo == "cam" else "fala_bat.json"
            try:
                with open(os.path.join(DIRETORIO_DADOS, arquivo), "w", encoding="utf-8") as f:
                    json.dump({"enabled": novo_estado}, f)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        if parsed.path == "/api/upload":
            nome = data.get("nome")
            conteudo_b64 = data.get("conteudo")
            if nome and conteudo_b64:
                try:
                    caminho_final = os.path.join("/sdcard/servidor", os.path.basename(nome))
                    with open(caminho_final, "wb") as f:
                        f.write(base64.b64decode(conteudo_b64))
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"success": true}')
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        if parsed.path == "/api/deletar":
            arquivo = data.get("arquivo")
            if arquivo and ".." not in arquivo and arquivo.startswith("dados/videos/"):
                try:
                    if os.path.exists(arquivo):
                        os.remove(arquivo)
                    nome_video = os.path.basename(arquivo)
                    thumb_assoc = os.path.join(DIRETORIO_THUMBS, f"{nome_video}.jpg")
                    if os.path.exists(thumb_assoc):
                        os.remove(thumb_assoc)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"success": true}')
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        if parsed.path == "/api/deletar_pasta":
            dia = data.get("dia")
            if dia:
                try:
                    pasta_videos = os.path.join(DIRETORIO_DADOS, "videos")
                    if os.path.exists(pasta_videos):
                        for f in os.listdir(pasta_videos):
                            if f.endswith('.mp4'):
                                caminho_completo = os.path.join(pasta_videos, f)
                                m = re.match(r'(\d{4})-(\d{2})-(\d{2})_', f)
                                if m:
                                    raw_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
                                    fmt_date = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
                                    if dia in (raw_date, fmt_date):
                                        if os.path.exists(caminho_completo):
                                            os.remove(caminho_completo)
                                        thumb_assoc = os.path.join(DIRETORIO_THUMBS, f"{f}.jpg")
                                        if os.path.exists(thumb_assoc):
                                            os.remove(thumb_assoc)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"success": true}')
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        if parsed.path == "/api/deletar_multiplos":
            arquivos = data.get("arquivos", [])
            if isinstance(arquivos, list):
                try:
                    for arq in arquivos:
                        if arq and ".." not in arq and arq.startswith("dados/videos/"):
                            if os.path.exists(arq):
                                os.remove(arq)
                            nome_v = os.path.basename(arq)
                            thumb_a = os.path.join(DIRETORIO_THUMBS, f"{nome_v}.jpg")
                            if os.path.exists(thumb_a):
                                os.remove(thumb_a)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'{"success": true}')
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
                return

        if parsed.path == "/api/cortar":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"success": true}')
            subprocess.run("pkill -2 -f ffmpeg", shell=True)
            return

        if parsed.path == "/api/limpar_logs":
            try:
                with open(os.path.join(DIRETORIO_DADOS, "camlog.txt"), "w", encoding="utf-8") as f:
                    f.write("")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"success": true}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        if parsed.path == "/api/reboot_android":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"success": true}')
            threading.Thread(target=lambda: (time.sleep(1), subprocess.run("su -c 'reboot'", shell=True))).start()
            return

if __name__ == "__main__":
    t = threading.Thread(target=atualizador_de_thumb, daemon=True)
    t.start()
    
    server = ThreadedHTTPServer(("0.0.0.0", PORT), CFTVHandler)
    print(f"Servidor CFTV operando em http://0.0.0.0:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()