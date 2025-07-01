# gestion_choferes_google.py

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def gestion_choferes():
    st.title("🚚 Gestión de Chóferes – con Google Sheets")

    # Conectar con Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Leer datos
    df = conn.read(worksheet="TABLA COMPLETA", usecols=list(range(6)))  # Ajusta columnas si tienes más
    df = df.dropna(how="all")  # Eliminar filas vacías

    # Buscador por chófer
    search = st.text_input("🔍 Buscar por nombre de chófer:")
    if search:
        df = df[df["Chofer"].str.contains(search, case=False, na=False)]

    if df.empty:
        st.warning("No se encontraron registros.")
    else:
        for i, row in df.iterrows():
            st.markdown("---")
            st.subheader(f"👤 {row['Chofer']}")

            tractora = st.text_input("🚛 Matrícula tractora", value=row["Matr Tractora"], key=f"tractora_{i}")
            remolque = st.text_input("🛻 Matrícula remolque", value=row["Matr Remolque"], key=f"remolque_{i}")
            estado = st.text_input("📍 Estado", value=row["ESTADO"], key=f"estado_{i}")

            if st.button("💾 Guardar cambios", key=f"guardar_{i}"):
                df.at[i, "Matr Tractora"] = tractora
                df.at[i, "Matr Remolque"] = remolque
                df.at[i, "ESTADO"] = estado
                conn.update(worksheet="TABLA COMPLETA", data=df)
                st.success("✅ Registro actualizado correctamente.")
