import streamlit as st
import pandas as pd

# Cargar los datos desde el Excel
@st.cache_data
def load_data():
    choferes = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Chóferes")
    remolques = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Remolques")
    tractoras = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Tractoras")
    return choferes, remolques, tractoras

choferes_df, remolques_df, tractoras_df = load_data()

st.title("🔍 Consulta de matrículas")
matricula_input = st.text_input("Introduce una matrícula de tractora o remolque:").upper().strip()

if matricula_input:
    # Buscar si es tractora
    tractora_row = tractoras_df[tractoras_df["Matrícula"] == matricula_input]
    if not tractora_row.empty:
        chofer = tractora_row.iloc[0]["Chofer asignado"]
        remolque = tractora_row.iloc[0]["Remolque asignado"]
        jefe = choferes_df[choferes_df["Chofer"] == chofer]["Jefe de tráfico"].values[0] if chofer in choferes_df["Chofer"].values else "Desconocido"
        st.success(f"La tractora {matricula_input} la conduce {chofer} junto al remolque {remolque} y su jefe de tráfico es {jefe}.")

    else:
        # Buscar si es remolque
        remolque_row = remolques_df[remolques_df["Matrícula"] == matricula_input]
        if not remolque_row.empty:
            chofer = remolque_row.iloc[0]["Chofer asignado"]
            tractora = remolque_row.iloc[0]["Tractora asignada"]
            jefe = choferes_df[choferes_df["Chofer"] == chofer]["Jefe de tráfico"].values[0] if chofer in choferes_df["Chofer"].values else "Desconocido"
            st.success(f"El remolque {matricula_input} está asignado a {chofer}, que conduce la tractora {tractora} bajo la supervisión de {jefe}.")
        else:
            st.error("Matrícula no encontrada en el sistema.")
