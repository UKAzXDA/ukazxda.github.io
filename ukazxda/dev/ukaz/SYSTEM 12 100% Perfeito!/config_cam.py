import urllib.request
import datetime
import os
import sys
# Camera iM6 Full Color
CAMERA_IP = "192.168.1.7"
USUARIO = "admin"
ARQUIVO_LOG = "/sdcard/servidor/dados/camlog.txt"
CAMINHO_SENHA_SEGURA = "/data/data/com.termux/files/home/.senha_cftv"

def obter_senha():
    if not os.path.exists(CAMINHO_SENHA_SEGURA):
        registrar_log("🚨 Arquivo de senha não encontrado!")
        sys.exit(1)
    try:
        with open(CAMINHO_SENHA_SEGURA, "r", encoding="utf-8") as f:
            senha = f.read().strip()
        if not senha:
            registrar_log("🚨 Senha vazia!")
            sys.exit(1)
        return senha
    except Exception as e:
        registrar_log(f"🚨 Erro na senha: {e}")
        sys.exit(1)

SENHA = obter_senha()

def registrar_log(mensagem):
    data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linha = f"{mensagem} ({data_hora})" 
    print(linha)
    
    os.makedirs(os.path.dirname(ARQUIVO_LOG), exist_ok=True)
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

def requisicao_api(url):
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, USUARIO, SENHA)
    authhandler = urllib.request.HTTPDigestAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    try:
        resposta = opener.open(url, timeout=5)
        return resposta.read().decode('utf-8')
    except Exception as e:
        registrar_log(f"❌ Erro de conexão com a câmera {CAMERA_IP}: {e}")
        return None

def iniciar_verificacao():
    registrar_log("🔍 Forçando configuração total de qualidade e H.264 na câmera...")
    parametros = (
        "&Encode[0].MainFormat[0].Video.Compression=H.264"
        "&Encode[0].MainFormat[0].Video.SmartCodec=false"
        "&Encode[0].MainFormat[0].Video.Profile=High"
        "&Encode[0].MainFormat[0].Video.BitRate=2048"
        "&Encode[0].MainFormat[0].Video.FPS=30"
        "&Encode[0].MainFormat[0].Video.Resolution=VGA"
        "&Encode[0].MainFormat[0].Audio.Compression=AAC"
        "&Encode[0].MainFormat[0].Audio.Frequency=16000"
        "&Encode[0].MainFormat[0].AudioEnable=true"
        "&Encode[0].MainFormat[1].Video.Compression=H.264"
        "&Encode[0].MainFormat[1].Video.SmartCodec=false"
        "&Encode[0].MainFormat[2].Video.Compression=H.264"
        "&Encode[0].MainFormat[2].Video.SmartCodec=false"
        "&Encode[0].ExtraFormat[0].Video.Compression=H.264"
        "&Encode[0].ExtraFormat[0].Video.SmartCodec=false"
        "&Encode[0].ExtraFormat[0].Video.Profile=Main"
        "&Encode[0].ExtraFormat[0].Video.BitRate=1024"
        "&Encode[0].ExtraFormat[0].Audio.Compression=AAC"
        "&Encode[0].ExtraFormat[0].AudioEnable=true"
    )
    url_set = f"http://{CAMERA_IP}/cgi-bin/configManager.cgi?action=setConfig{parametros}"
    resultado_set = requisicao_api(url_set)

    if resultado_set and "OK" in resultado_set:
        registrar_log("🚀 Sucesso! Câmera reconfigurada com qualidade ajustada para 480P@30 (VGA) e H.264 Puro.")
    else:
        registrar_log("❌ Falhou ao tentar gravar a nova configuração na câmera.")

if __name__ == "__main__":
    iniciar_verificacao()