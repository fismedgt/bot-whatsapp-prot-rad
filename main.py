from fastapi import FastAPI, Request
import requests
from agente import agente_ventas

app = FastAPI()

# =========================
# CONFIGURACIÓN
# =========================
import os

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# =========================
# RUTA BASE
# =========================
@app.get("/")
def root():
    return {"status": "ok"}

# =========================
# VERIFICACIÓN WEBHOOK
# =========================
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge"))

    return "Error de verificación"

# =========================
# RECEPCIÓN DE MENSAJES
# =========================
@app.post("/webhook")
async def receive_message(request: Request):
    try:
        # 🔥 PROTEGER PARSEO JSON
        try:
            data = await request.json()
        except Exception as e:
            print("🔥 ERROR JSON:", e)
            return {"status": "error json"}

        print("📩 DATA COMPLETA:", data)

        entry = data.get("entry", [])
        if not entry:
            return {"status": "no entry"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "no changes"}

        value = changes[0].get("value", {})
        messages = value.get("messages")

        if not messages:
            print("⚠️ Evento sin mensaje")
            return {"status": "no message"}

        message = messages[0]

        if message.get("type") != "text":
            print("⚠️ No es texto:", message)
            return {"status": "ignored"}

        texto = message.get("text", {}).get("body", "")
        telefono = message.get("from", "")

        print(f"📲 Mensaje recibido de {telefono}: {texto}")

        # 🔥 PROTEGER AGENTE
        try:
            respuesta = agente_ventas(texto, telefono)
        except Exception as e:
            print("🔥 ERROR AGENTE:", e)
            respuesta = "Error procesando mensaje"

        # 🔥 PROTEGER ENVÍO
        try:
            enviar_mensaje(telefono, respuesta)
        except Exception as e:
            print("🔥 ERROR ENVÍO:", e)

        return {"status": "ok"}

    except Exception as e:
        print("🔥 ERROR CRÍTICO TOTAL:", e)
        return {"status": "fatal"}

# =========================
# ENVÍO DE MENSAJES
# =========================
def enviar_mensaje(numero, texto):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }

    response = requests.post(url, headers=headers, json=data)

    print("📤 Respuesta envío:", response.status_code, response.text)
