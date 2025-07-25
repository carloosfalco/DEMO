import streamlit as st
from streamlit_chat import message
import requests
import uuid

def consulta_matriculas():
    st.title("🔎 Consulta de matrículas")
    st.markdown("Escribe una consulta en lenguaje natural para saber quién lleva una tractora, remolque o qué tiene un chófer asignado.")

    # Ruta pública del logo de Virosque
    logo_virosque = "https://raw.githubusercontent.com/carloosfalco/DEMO/main/logo-virosque2-01.png"

    # Función para consultar al webhook de Make
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

    # Inicializar historial
    if "chat_matriculas" not in st.session_state:
        st.session_state.chat_matriculas = []

    # Entrada del usuario
    user_input = st.chat_input("¿Qué quieres consultar?")
    if user_input:
        st.session_state.chat_matriculas.append({"role": "user", "content": user_input})
        respuestas = obtener_respuesta(user_input)
        for r in respuestas:
            st.session_state.chat_matriculas.append({"role": "assistant", "content": r})

    # Mostrar el historial
    for msg in st.session_state.chat_matriculas:
        if isinstance(msg, dict) and "content" in msg and "role" in msg:
            if msg["role"] == "user":
                with st.container():
                    cols = st.columns([0.1, 0.9])
                    with cols[0]:
                        st.image(logo_virosque, width=40)
                    with cols[1]:
                        st.markdown(
                            f"""
                            <div style='padding:10px 15px; background-color:#f0f2f6;
                                        border-radius:10px; color:#000000;
                                        font-size:16px; line-height:1.5;'>
                                {msg['content']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                message(msg["content"], is_user=False, key=f"msg_{uuid.uuid4()}")
