import streamlit as st
import pandas as pd
from datetime import datetime
import json
from google.oauth2 import service_account
import gspread

def consulta_matriculas():
    st.title("🤖 Instrucciones para usar el Bot de Telegram")
    st.markdown("""
    Ahora puedes realizar consultar a cerca de tractoras o remolques desde Telegram.

    ### 👉 ¿Cómo usar el bot?
    1. Abre la app de Telegram.
    2. Busca el bot por su nombre: `@virosque_consulta_bot`.
    3. Introduce la contraseña VrTc4489
    4. Puedes escribirle en lenguaje natural cosas como:
        - `¿Quién lleva la 2243?`
        - `¿Quién lleva el remolque R6654BCD?`
    5. El bot responderá a tu consulta.
    """)
