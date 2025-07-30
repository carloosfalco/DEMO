import streamlit as st
import requests

def consulta_matriculas():
    st.title("🔎 Consulta de matrículas")
    st.markdown(
        "Escribe una consulta en lenguaje natural para saber quién lleva una tractora, "
        "remolque o qué tiene un chófer asignado."
    )

    avatar_user = "https://raw.githubusercontent.com/carloosfalco/DEMO/main/logo_peque_virosque.png"
    avatar_bot = "https://raw.githubusercontent.com/carloosfalco/DEMO/main/robot_icon.png"  # puedes usar tu icono de bot

    # Función para obtener respuestas desde Make
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

    # Historial de chat
    if "chat_matriculas" not in st.session_state:
        st.session_state.chat_matriculas = []

    # Entrada de usuario
    user_input = st.chat_input("¿Qué quieres consultar?")
    if user_input:
        # Guardamos mensaje del usuario
        st.session_state.chat_matriculas.append({"role": "user", "content": user_input})

        # Consultamos webhook y añadimos respuesta(s)
        respuestas = obtener_respuestas(user_input)
        for r in respuestas:
            st.session_state.chat_matriculas.append({"role": "assistant", "content": r})

    # Mostrar historial con estilo tipo WhatsApp
    for msg in st.session_state.chat_matriculas:
        if msg["role"] == "user":
            with st.chat_message("user", avatar=avatar_user):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar=avatar_bot):
                st.markdown(msg["content"])
