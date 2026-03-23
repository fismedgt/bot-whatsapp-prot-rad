import streamlit as st
import json
import pandas as pd
import requests

CHAT_FILE = "chat_log.json"

st.set_page_config(page_title="CRM WhatsApp", layout="wide")

st.title("📲 Panel de Mensajes - WhatsApp Bot")

# 🔄 Cargar datos

API_URL = "https://bot-whatsapp-prot-rad.onrender.com/chats"

def cargar_datos():
    try:
        response = requests.get(API_URL)
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        print("Error cargando datos:", e)
        return pd.DataFrame()

df = cargar_datos()
st.write("DEBUG DATA:", df)

if df.empty:
    st.warning("No hay mensajes aún")
else:
    # 📊 Lista de números únicos
    numeros = df["numero"].unique()

    numero_seleccionado = st.sidebar.selectbox("Selecciona un cliente", numeros)

    chat_cliente = df[df["numero"] == numero_seleccionado]

    st.subheader(f"Conversación con {numero_seleccionado}")

    for _, row in chat_cliente.iterrows():
        if row["tipo"] == "recibido":
            st.markdown(f"**👤 Cliente:** {row['texto']}")
        else:
            st.markdown(f"**🤖 Bot:** {row['texto']}")

    st.markdown("---")

    # ✍️ Enviar mensaje manual
    mensaje_manual = st.text_input("Escribe un mensaje")

    if st.button("Enviar"):
        st.success("Aquí luego conectamos con el backend 😏")
