import streamlit as st
import pandas as pd
from datetime import datetime
import re

def normalizar_tractora(input_txt):
    # Acepta solo números y completa con letras por defecto
    match = re.match(r"^\d{4}", input_txt)
    return input_txt if not match else f"{match.group()}NBM"

def normalizar_remolque(input_txt):
    # Acepta formato R+4 números
    match = re.match(r"^R\d{4}", input_txt)
    return match.group() if match else input_txt

def consulta_matriculas():
    st.title("🔍 Consulta de matrículas")

    @st.cache_data
    def load_data():
        choferes = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Chóferes")
        remolques = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Remolques")
        tractoras = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Tractoras")
        return choferes, remolques, tractoras

    choferes_df, remolques_df, tractoras_df = load_data()

    matricula_input = st.text_input("Introduce una matrícula de tractora o remolque:").upper().strip()

    if matricula_input:
        tractora_input = normalizar_tractora(matricula_input)
        remolque_input = normalizar_remolque(matricula_input)

        tractora_row = tractoras_df[tractoras_df["Matrícula"] == tractora_input]
        if not tractora_row.empty:
            chofer = tractora_row.iloc[0]["Chofer asignado"]
            remolque = tractora_row.iloc[0]["Remolque asignado"]
            jefe = choferes_df[choferes_df["Chofer"] == chofer]["Jefe de tráfico"].values[0] if chofer in choferes_df["Chofer"].values else "Desconocido"
            tipo_remolque = remolques_df[remolques_df["Matrícula"] == remolque]["Tipo"].values[0] if remolque in remolques_df["Matrícula"].values else "Desconocido"
            st.success(f"La tractora {tractora_input} la conduce {chofer} junto al remolque {remolque} (tipo {tipo_remolque}) y su jefe de tráfico es {jefe}.")
        else:
            remolque_row = remolques_df[remolques_df["Matrícula"] == remolque_input]
            if not remolque_row.empty:
                chofer = remolque_row.iloc[0]["Chofer asignado"]
                tractora = remolque_row.iloc[0]["Tractora asignada"]
                tipo = remolque_row.iloc[0]["Tipo"]
                jefe = choferes_df[choferes_df["Chofer"] == chofer]["Jefe de tráfico"].values[0] if chofer in choferes_df["Chofer"].values else "Desconocido"
                st.success(f"El remolque {remolque_input} (tipo {tipo}) está asignado a {chofer}, que conduce la tractora {tractora} bajo la supervisión de {jefe}.")
            else:
                st.error("Matrícula no encontrada en el sistema.")

    # Resto del código continúa igual... (no se muestra para ahorrar espacio)
    # Solo se han modificado las entradas para que funcionen con normalización
    # en tractora (solo números) y remolque (R + 4 cifras)
