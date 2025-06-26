import streamlit as st
import pandas as pd
from datetime import datetime

REMOLQUES_FILE = "remolques.csv"
MANTENIMIENTOS_FILE = "mantenimientos.csv"

def cargar_datos():
    try:
        remolques = pd.read_csv(REMOLQUES_FILE)
    except FileNotFoundError:
        remolques = pd.DataFrame(columns=["matricula", "tipo", "parking", "chofer", "fecha", "estado"])
    try:
        mantenimientos = pd.read_csv(MANTENIMIENTOS_FILE)
    except FileNotFoundError:
        mantenimientos = pd.DataFrame(columns=["matricula", "tipo_mantenimiento"])
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
        accion = st.radio("¿Qué quieres registrar?", ["Entrada a mantenimiento", "Fin de mantenimiento", "Asignación a chófer"])

        if accion == "Entrada a mantenimiento":
            matricula = st.selectbox("Selecciona matrícula", remolques["matricula"])
            tipo_mant = st.text_input("Descripción del mantenimiento")
            if st.button("Registrar entrada"):
                if matricula not in mantenimientos["matricula"].values:
                    nuevo = pd.DataFrame([{"matricula": matricula, "tipo_mantenimiento": tipo_mant}])
                    mantenimientos = pd.concat([mantenimientos, nuevo], ignore_index=True)
                    remolques.loc[remolques["matricula"] == matricula, "estado"] = "mantenimiento"
                    guardar_datos(remolques, mantenimientos)
                    st.success(f"Remolque {matricula} registrado en mantenimiento.")
                else:
                    st.warning("Ese remolque ya está en mantenimiento.")

        elif accion == "Fin de mantenimiento":
            matricula = st.selectbox("Selecciona matrícula en taller", mantenimientos["matricula"])
            if st.button("Marcar como disponible"):
                mantenimientos = mantenimientos[mantenimientos["matricula"] != matricula]
                remolques.loc[remolques["matricula"] == matricula, "estado"] = "disponible"
                remolques.loc[remolques["matricula"] == matricula, "fecha"] = datetime.today().strftime('%Y-%m-%d')
                guardar_datos(remolques, mantenimientos)
                st.success(f"Remolque {matricula} marcado como disponible.")

        elif accion == "Asignación a chófer":
            matricula = st.selectbox("Selecciona matrícula disponible", remolques[remolques["estado"] == "disponible"]["matricula"])
            chofer = st.text_input("Nombre del chófer")
            if st.button("Asignar remolque"):
                remolques.loc[remolques["matricula"] == matricula, "estado"] = "asignado"
                remolques.loc[remolques["matricula"] == matricula, "chofer"] = chofer
                remolques.loc[remolques["matricula"] == matricula, "fecha"] = datetime.today().strftime('%Y-%m-%d')
                guardar_datos(remolques, mantenimientos)
                st.success(f"Remolque {matricula} asignado a {chofer}.")
