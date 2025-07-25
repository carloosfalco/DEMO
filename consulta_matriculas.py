import streamlit as st
from streamlit_chat import message
import requests
import uuid

def consulta_matriculas():
    st.title("🔎 Consulta de matrículas")
    st.markdown("Escribe una consulta en lenguaje natural para saber quién lleva una tractora, remolque o qué tiene un chófer asignado.")

    # Nuevo logo (enlace RAW desde GitHub)
    logo_virosque = "https://raw.githubusercontent.com/carloosfalco/DEMO/main/logo_peque_virosque.png"

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

    # Inicializar historial de conversación
    if "chat_matriculas" not in st.session_state:
        st.session_state.chat_matriculas = []

    # Entrada del usuario
    user_input = st.chat_input("¿Qué quieres consultar?")
    if user_input:
        st.session_state.chat_matriculas.append({"role": "user", "content": user_input})
        respuestas = obtener_respuesta(user_input)
        for r in respuestas:
            st.session_state.chat_matriculas.append({"role": "assistant", "content": r})

    # Mostrar historial del chat
    for msg in st.session_state.chat_matriculas:
        if isinstance(msg, dict) and "content" in msg and "role" in msg:
            if msg["role"] == "user":
                # Mensaje del usuario alineado a la derecha con el logo
                st.markdown(
                    f"""
                    <div style='display: flex; justify-content: flex-end; align-items: center; margin-top: 10px;'>
                        <div style='background-color:#f0f2f6; color:#000; padding:10px 15px;
                                    border-radius:10px; max-width: 70%; font-size:16px;
                                    line-height:1.5; word-wrap: break-word; text-align: left;'>
                            {msg["content"]}
                        </div>
                        <img src="{logo_virosque}" width="40" style="margin-left: 8px; border-radius: 50%;" />
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                # Mensaje del bot (estilo clásico)
                message(msg["content"], is_user=False, key=f"msg_{uuid.uuid4()}")
