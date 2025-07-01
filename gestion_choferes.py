import streamlit as st
import pandas as pd
import os

CSV_FILE = "choferes.csv"

def gestion_choferes():
    st.title("🚚 Gestión de Chóferes – desde CSV")

    # Cargar datos
    if not os.path.exists(CSV_FILE):
        st.error(f"No se encuentra el archivo {CSV_FILE}")
        return

    df = pd.read_csv(CSV_FILE)
    df = df.dropna(how="all")

    search = st.text_input("🔍 Buscar por nombre de chófer:")
    if search:
        df_filtered = df[df["Chofer"].str.contains(search, case=False, na=False)]
    else:
        df_filtered = df.copy()

    if df_filtered.empty:
        st.warning("No se encontraron registros.")
    else:
        for i, row in df_filtered.iterrows():
            st.markdown("---")
            st.subheader(f"👤 {row['Chofer']}")

            tractora = st.text_input("🚛 Matrícula tractora", value=row["Matr Tractora"], key=f"tractora_{i}")
            remolque = st.text_input("🛻 Matrícula remolque", value=row["Matr Remolque"], key=f"remolque_{i}")
            estado = st.text_input("📍 Estado", value=row["ESTADO"], key=f"estado_{i}")

            if st.button("💾 Guardar cambios", key=f"guardar_{i}"):
                df.at[i, "Matr Tractora"] = tractora
                df.at[i, "Matr Remolque"] = remolque
                df.at[i, "ESTADO"] = estado
                df.to_csv(CSV_FILE, index=False)
                st.success("✅ Registro actualizado correctamente.")
