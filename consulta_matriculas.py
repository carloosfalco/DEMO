import streamlit as st
import requests

def consulta_matriculas():
    st.title("🔎 Consulta de matrículas")
    st.markdown(
        "Escribe una consulta en lenguaje natural para saber quién lleva una tractora, "
        "remolque o qué tiene un chófer asignado."
    )

    avatar_user = "https://raw.githubusercontent.com/carloosfalco/DEMO/main/logo_peque_virosque.png"
    avatar_bot = "https://raw.githubusercontent.com/carloosfalco/DEMO/main/chip-de-ia.png"

    # CSS estilo WhatsApp
    st.markdown("""
        <style>
        .chat-container {
            width: 100%;
            overflow: hidden;
            margin: 10px 0;
            display: flex;
        }
        .chat-bubble {
            max-width: 65%;
            padding: 10px 15px;
            border-radius: 15px;
            line-height: 1.4;
            word-wrap: break-word;
        }
        .user-bubble {
            background-color: #DCF8C6;
            margin-left: auto;
            border-bottom-right-radius: 2px;
        }
        .bot-bubble {
            background-color: #F1F0F0;
            margin-right: auto;
            border-bottom-left-radius: 2px;
        }
        .chat-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
        }
        .user-msg {
            justify-content: flex-end;
        }
        .bot-msg {
            justify-content: flex-start;
        }
        </style>
    """, unsafe_allow_html=True)

    # Función para obtener respuestas desde Make
    def obtener_respuestas(input_usuario):
        url_webhook = "https://hook.eu2.make.com/qaddp62g48t3d3dveklxvrso898d6774"

        try:
            respuesta = requests.post(
                url_webhook,
                json={"consulta": input_usuario},
                timeout=300
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
        st.session_state.chat_matriculas.append({"role": "user", "content": user_input})

        respuestas = obtener_respuestas(user_input)
        for r in respuestas:
            st.session_state.chat_matriculas.append({"role": "assistant", "content": r})

    # Mostrar historial con avatares en el lado correcto
    for msg in st.session_state.chat_matriculas:
        if msg["role"] == "user":
            # Burbuja + avatar a la derecha
            st.markdown(
                f"""
                <div class="chat-container user-msg">
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                    <img src="{avatar_user}" class="chat-avatar" style="margin-left:5px;">
                </div>
                """, unsafe_allow_html=True
            )
        else:
            # Avatar + burbuja a la izquierda
            st.markdown(
                f"""
                <div class="chat-container bot-msg">
                    <img src="{avatar_bot}" class="chat-avatar" style="margin-right:5px;">
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True
            )
