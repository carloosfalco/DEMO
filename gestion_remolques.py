import streamlit as st
import pandas as pd
from datetime import datetime

REMOLQUES_FILE = "data/remolques.csv"
MANTENIMIENTOS_FILE = "data/mantenimientos.csv"

def cargar_datos():
    try:
        remolques = pd.read_csv(REMOLQUES_FILE)
    except FileNotFoundError:
        remolques = pd.DataFrame(columns=["matricula", "tipo", "estado", "parking", "chofer", "fecha"])
    try:
        mantenimientos = pd.read_csv(MANTENIMIENTOS_FILE)
    except FileNotFoundError:
        mantenimientos = pd.DataFrame(columns=["matricula", "tipo_mantenimiento", "fecha_inicio", "fecha_fin"])
    return remolques, mantenimientos

def guardar_datos(remolques, mantenimientos):
    remolques.to_csv(REMOLQUES_FILE, index=False)
    mantenimientos.to_csv(MANTENIMIENTOS_FILE, index=False)

def gestion_remolques():
    st.title("🛠 Gestión de Remolques")

    remolques, mantenimientos = cargar_datos()

    tab1, tab2, tab3 = st.tabs(["📋 Disponibles", "🧰 En mantenimiento", "➕ Registrar movimiento"])

    with tab1:
        st.subheader("Remolques disponibles")
        st.dataframe(remolques[remolques["estado"] == "disponible"])

    with tab2:
        st.subheader("Remolques en mantenimiento")
        st.dataframe(mantenimientos)

    with tab3:
        st.subheader("Registrar entrada o salida")
        opcion = st.radio("Tipo de movimiento", ["Entrada en mantenimiento", "Fin de mantenimiento", "Asignación a chófer"])

        if opcion == "Entrada en mantenimiento":
            matricula = st.text_input("Matrícula del remolque")
            tipo_mant = st.text_input("Tipo de mantenimiento")
            if st.button("Registrar entrada"):
                nueva_entrada = pd.DataFrame([{
                    "matricula": matricula,
                    "tipo_mantenimiento": tipo_mant,
                    "fecha_inicio": datetime.today().strftime('%Y-%m-%d'),
                    "fecha_fin": ""
                }])
                mantenimientos = pd.concat([mantenimientos, nueva_entrada], ignore_index=True)
                remolques.loc[remolques["matricula"] == matricula, "estado"] = "mantenimiento"
                guardar_datos(remolques, mantenimientos)
                st.success("Entrada en mantenimiento registrada.")

        elif opcion == "Fin de mantenimiento":
            matricula = st.selectbox("Selecciona matrícula", mantenimientos["matricula"].unique())
            if st.button("Marcar como disponible"):
                remolques.loc[remolques["matricula"] == matricula, "estado"] = "disponible"
                remolques.loc[remolques["matricula"] == matricula, "fecha"] = datetime.today().strftime('%Y-%m-%d')
                mantenimientos = mantenimientos[mantenimientos["matricula"] != matricula]
                guardar_datos(remolques, mantenimientos)
                st.success("Remolque marcado como disponible.")

        elif opcion == "Asignación a chófer":
            matricula = st.selectbox("Selecciona matrícula disponible", remolques[remolques["estado"] == "disponible"]["matricula"])
            chofer = st.text_input("Nombre del chófer")
            if st.button("Asignar remolque"):
                remolques.loc[remolques["matricula"] == matricula, "estado"] = "asignado"
                remolques.loc[remolques["matricula"] == matricula, "chofer"] = chofer
                remolques.loc[remolques["matricula"] == matricula, "fecha"] = datetime.today().strftime('%Y-%m-%d')
                guardar_datos(remolques, mantenimientos)
                st.success("Remolque asignado correctamente.")
