import streamlit as st
from streamlit_chat import message
import requests
import uuid

def consulta_matriculas():
    st.title("🔎 Consulta de matrículas")
    st.markdown("Escribe una consulta en lenguaje natural para saber quién lleva una tractora, remolque o qué tiene un chófer asignado.")

    # URL del webhook de Make
    url_webhook = "https://hook.eu2.make.com/vkzk2hkl67dn1d5gyszmbjn8duoyi9c3"

    # Logo de Virosque como avatar del bot
    logo_virosque = "https://raw.githubusercontent.com/carloosfalco/DEMO/main/logo-virosque2-01.png"

    # Función que consulta a Make y devuelve una lista de respuestas
    def obtener_respuesta(input_usuario):
        try:
            respuesta = requests.post(
                url_webhook,
                json={"consulta": input_usuario},
                timeout=20
            )

            if respuesta.status_code == 200:
                datos = respuesta.json()
                raw = datos.get("respuesta")

                # Dividir si hay múltiples líneas
                if isinstance(raw, str):
                    return [linea.strip() for linea in raw.split("\n") if linea.strip()]
                elif isinstance(raw, list):
                    return raw
                else:
                    return ["⚠️ La respuesta está vacía."]
            else:
                return [f"⚠️ Error {respuesta.status_code} al conectar con Make."]
        except requests.exceptions.Timeout:
            return ["⚠️ Tiempo de espera agotado. Make tardó demasiado en responder."]
        except Exception as e:
            return [f"⚠️ Error de conexión: {str(e)}"]

    # Inicializar historial del chat
    if "chat_matriculas" not in st.session_state:
        st.session_state.chat_matriculas = []

    # Entrada del usuario
    user_input = st.chat_input("¿Qué quieres consultar?")
    if user_input:
        st.session_state.chat_matriculas.append({"role": "user", "content": user_input})
        respuestas = obtener_respuesta(user_input)
        for r in respuestas:
            st.session_state.chat_matriculas.append({"role": "assistant", "content": r})

    # Mostrar historial con avatar personalizado
    for msg in st.session_state.chat_matriculas:
        message(
            msg["content"],
            is_user=(msg["role"] == "user"),
            avatar=None if msg["role"] == "user" else logo_virosque,
            key=f"msg_{uuid.uuid4()}"
        )
