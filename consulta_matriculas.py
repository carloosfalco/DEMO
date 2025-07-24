import streamlit as st
from streamlit_chat import message
import requests

def consulta_matriculas():
    st.title("🔎 Consulta de matrículas")
    st.markdown("Escribe una consulta en lenguaje natural para saber quién lleva una tractora, remolque o qué tiene un chófer asignado.")

    # Función que se conecta al webhook de Make
    def obtener_respuesta(input_usuario):
        url_webhook = "https://hook.eu2.make.com/vkzk2hkl67dn1d5gyszmbjn8duoyi9c3"

        try:
            respuesta = requests.post(
                url_webhook,
                json={"consulta": input_usuario},
                timeout=10
            )

            if respuesta.status_code == 200:
                datos = respuesta.json()
                return datos.get("respuesta", "⚠️ La respuesta no tiene contenido.")
            else:
                return f"⚠️ Error {respuesta.status_code} al conectar con Make."

        except Exception as e:
            return f"⚠️ Error de conexión: {str(e)}"

    # Inicializar historial del chat
    if "chat_matriculas" not in st.session_state:
        st.session_state.chat_matriculas = []

    # Caja de entrada del usuario
    user_input = st.chat_input("¿Qué quieres consultar?")
    if user_input:
        st.session_state.chat_matriculas.append({"role": "user", "content": user_input})
        respuesta = obtener_respuesta(user_input)
        st.session_state.chat_matriculas.append({"role": "assistant", "content": respuesta})

    # Mostrar el historial del chat con claves únicas
    for i, msg in enumerate(st.session_state.chat_matriculas):
        message(msg["content"], is_user=(msg["role"] == "user"), key=f"msg_{i}")
