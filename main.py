from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import requests
import os
import json
from datetime import datetime

CHAT_FILE = "chat_log.json"

app = FastAPI()

import json

@app.get("/chats")
def get_chats():
    try:
        with open("chat_log.json", "r") as f:
            data = json.load(f)
        return data
    except:
        return []


# 🔑 CONFIGURACIÓN (MEJOR usar variables de entorno en Render)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mi_token_seguro")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "tu_access_token")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "tu_phone_number_id")

# 🧠 Memoria simple (luego puedes cambiar a base de datos)
chat_log = []

# =========================================
# 🔐 VERIFICACIÓN DEL WEBHOOK (GET)
# =========================================
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    verify_token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    print("🔍 VERIFY_TOKEN RECIBIDO:", verify_token)
    print("🔍 VERIFY_TOKEN SERVIDOR:", VERIFY_TOKEN)
    print("🔍 CHALLENGE:", challenge)

    if verify_token == VERIFY_TOKEN and challenge:
        return PlainTextResponse(content=str(challenge), status_code=200)

    return JSONResponse({"error": "Token inválido"}, status_code=403)

# =========================================
# 📩 RECEPCIÓN DE MENSAJES (POST)
# =========================================
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    try:
        entry = data.get("entry", [])
        if not entry:
            return {"status": "no entry"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "no changes"}

        value = changes[0].get("value", {})
        messages = value.get("messages")

        if messages:
            message = messages[0]
            numero = message["from"]

            # 📩 Texto del mensaje
            texto = message.get("text", {}).get("body", "")

            print(f"📲 Mensaje recibido de {numero}: {texto}")

            guardar_mensaje(numero, texto, "recibido")

            # 💾 Guardar mensaje
            chat_log.append({
                "numero": numero,
                "mensaje": texto
            })

            # 🤖 Lógica de respuesta básica
            respuesta = generar_respuesta(texto)

            # 📤 Enviar respuesta
            send_whatsapp_message(numero, respuesta)

        return {"status": "ok"}

    except Exception as e:
        print("❌ ERROR PROCESANDO MENSAJE:", str(e))
        return {"status": "error"}

# =========================================
# 🤖 LÓGICA DE RESPUESTA
# =========================================
def generar_respuesta(texto):
    texto = texto.lower()

    if "hola" in texto or "buenos" in texto:
        return "Hola 👋 Bienvenido al asistente de protección radiológica. ¿En qué puedo ayudarte hoy?"

    elif "precio" in texto:
        return "Ofrecemos servicios de asesoría en protección radiológica. ¿Qué tipo de equipo utilizas?"

    elif "rayos x" in texto:
        return "Podemos apoyarte con cumplimiento normativo, blindaje y control de calidad en rayos X."

    else:
        return "Gracias por tu mensaje. En breve uno de nuestros especialistas te atenderá."

# =========================================
# 📤 ENVÍO DE MENSAJES A WHATSAPP
# =========================================
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=data)

    print("📤 STATUS:", response.status_code)
    print("📤 RESPUESTA:", response.text)

    if response.status_code == 200:
        guardar_mensaje(to, message, "enviado")
    else:
        print("❌ No se guardó porque falló el envío")

# =========================================
# 🧪 GUARDAR MENSAJES
# =========================================

def guardar_mensaje(numero, texto, tipo):
    mensaje = {
        "numero": numero,
        "texto": texto,
        "tipo": tipo,  # "recibido" o "enviado"
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open(CHAT_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(mensaje)

    with open(CHAT_FILE, "w") as f:
        json.dump(data, f, indent=2)

# =========================================
# 🧪 RUTA DE PRUEBA
# =========================================
@app.get("/")
async def root():
    return {"mensaje": "Servidor WhatsApp activo 🚀"}
