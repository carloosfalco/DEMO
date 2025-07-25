import streamlit as st
from streamlit_chat import message
import requests
import uuid

def consulta_matriculas():
    st.title("🔎 Consulta de matrículas")
    st.markdown("Escribe una consulta en lenguaje natural para saber quién lleva una tractora, remolque o qué tiene un chófer asignado.")

    # Ruta al logo local
    logo_virosque = "logo-virosque2-01.png"

    # Función que se conecta al webhook de Make
    def obtener_respuesta(input_usuario):
        url_webhook = "https://hook.eu2.make.com/vkzk2hkl67dn1d5gyszmbjn8duoyi9c3"

        try:
            respuesta = requests.post(
                url_webhook,
                json={"consulta": input_usuario},
                timeout=60
            )

            if respuesta.status_code == 200:
                datos = respuesta.json()
                raw = datos.get("respuesta")
                if isinstance(raw, str):
                    return [linea.strip() for linea in raw.split("\n") if linea.strip()]
                else:
                    return [raw]
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

    # Mostrar historial con el logo como avatar en todos los mensajes
    for msg in st.session_state.chat_matriculas:
        if isinstance(msg, dict) and "content" in msg and "role" in msg:
            message(
                msg["content"],
                is_user=(msg["role"] == "user"),
                avatar=logo_virosque,
                key=f"msg_{uuid.uuid4()}"
            )
