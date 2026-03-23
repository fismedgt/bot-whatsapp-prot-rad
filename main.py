from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import requests
import os

from agente import agente_ventas

app = FastAPI()

# =========================
# CONFIGURACIÓN
# =========================
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
# VERIFICACIÓN WEBHOOK (FIX CLAVE)
# =========================
from fastapi import FastAPI, Request

app = FastAPI()

VERIFY_TOKEN = "mi_token_123"

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    verify_token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if verify_token == VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Token inválido"}

# =========================
# RECEPCIÓN DE MENSAJES
# =========================
@app.post("/webhook")
async def receive_message(request: Request):
    print("🔥 WEBHOOK ACTIVADO")

    try:
        data = await request.json()
        print("📩 DATA COMPLETA:", data)

        entry = data.get("entry", [])
        if not entry:
            return JSONResponse({"status": "no entry"})

        changes = entry[0].get("changes", [])
        if not changes:
            return JSONResponse({"status": "no changes"})

        value = changes[0].get("value", {})
        messages = value.get("messages")

        if not messages:
            print("⚠️ Evento sin mensaje")
            return JSONResponse({"status": "no message"})

        message = messages[0]

        if message.get("type") != "text":
            print("⚠️ Mensaje no es texto:", message)
            return JSONResponse({"status": "ignored"})

        texto = message.get("text", {}).get("body", "")
        telefono = message.get("from", "")

        print(f"📲 Mensaje recibido de {telefono}: {texto}")

        # =========================
        # AGENTE IA
        # =========================
        try:
            respuesta = agente_ventas(texto, telefono)
        except Exception as e:
            print("🔥 ERROR AGENTE:", e)
            respuesta = "Hubo un error procesando tu mensaje."

        # =========================
        # ENVÍO RESPUESTA
        # =========================
        try:
            enviar_mensaje(telefono, respuesta)
        except Exception as e:
            print("🔥 ERROR ENVÍO:", e)

        return JSONResponse({"status": "ok"})

    except Exception as e:
        print("🔥 ERROR CRÍTICO TOTAL:", e)
        return JSONResponse({"status": "fatal"})

# =========================
# ENVÍO DE MENSAJES
# =========================
def enviar_mensaje(numero, texto):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

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

    print("📤 Respuesta envío:", response.status_code)
    print("📤 Detalle:", response.text)
