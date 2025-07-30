import streamlit as st
from streamlit_chat import message
import requests
import uuid

def consulta_matriculas():
    st.title("🔎 Consulta de matrículas")
    st.markdown("Escribe una consulta en lenguaje natural para saber quién lleva una tractora, remolque o qué tiene un chófer asignado.")

    logo_virosque = "https://raw.githubusercontent.com/carloosfalco/DEMO/main/logo_peque_virosque.png"

    def obtener_respuestas(input_usuario):
        url_webhook = "https://hook.eu2.make.com/qaddp62g48t3d3dveklxvrso898d6774"

        try:
            respuesta = requests.post(
                url_webhook,
                json={"consulta": input_usuario},
                timeout=60
            )

            if respuesta.status_code == 200:
                try:
                    data = respuesta.json()
                    if isinstance(data, list):
                        return [d.get("respuesta", "⚠️ Sin contenido.") for d in data]
                    elif isinstance(data, dict):
                        return [data.get("respuesta", "⚠️ Sin contenido.")]
                    else:
                        return ["⚠️ Formato de respuesta inesperado."]
                except Exception as e:
                    return [f"⚠️ Error al analizar JSON: {str(e)}"]
            else:
                return [f"⚠️ Error {respuesta.status_code} al conectar con Make."]
        except requests.exceptions.Timeout:
            return ["⚠️ Tiempo de espera agotado."]
        except Exception as e:
            return [f"⚠️ Error de conexión: {str(e)}"]

    # Historial
    if "chat_matriculas" not in st.session_state:
        st.session_state.chat_matriculas = []

    # Entrada
    user_input = st.chat_input("¿Qué quieres consultar?")
    if user_input:
        st.session_state.chat_matriculas.append({"role": "user", "content": user_input})
        respuestas = obtener_respuestas(user_input)
        for r in respuestas:
            st.session_state.chat_matriculas.append({"role": "assistant", "content": r})

    # Mostrar mensajes
    for i, msg in enumerate(st.session_state.chat_matriculas):
        if msg["role"] == "user":
            message(
                msg["content"],
                is_user=True,
                avatar_style="",
                logo=logo_virosque,
                key=f"user_{i}"
            )
        else:
            message(
                msg["content"],
                is_user=False,
                key=f"bot_{i}"
            )
