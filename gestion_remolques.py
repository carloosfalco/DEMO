import streamlit as st
import pandas as pd
from datetime import datetime

REMOLQUES_FILE = "remolques.csv"
MANTENIMIENTOS_FILE = "mantenimientos.csv"
SUBTIPOS_FILE = "subtipos_remolques.csv"

def cargar_datos():
    try:
        remolques = pd.read_csv(REMOLQUES_FILE)
    except FileNotFoundError:
        remolques = pd.DataFrame(columns=["matricula", "tipo", "parking", "chofer", "fecha", "estado"])
    try:
        mantenimientos = pd.read_csv(MANTENIMIENTOS_FILE)
    except FileNotFoundError:
        mantenimientos = pd.DataFrame(columns=["matricula", "tipo_mantenimiento"])
    try:
        subtipos = pd.read_csv(SUBTIPOS_FILE)
    except FileNotFoundError:
        subtipos = pd.DataFrame(columns=["matricula", "subtipo"])
    return remolques, mantenimientos, subtipos

def guardar_datos(remolques, mantenimientos):
    remolques.to_csv(REMOLQUES_FILE, index=False)
    mantenimientos.to_csv(MANTENIMIENTOS_FILE, index=False)

def gestion_remolques():
    st.title("🛠 Gestión de Remolques")

    remolques, mantenimientos, subtipos = cargar_datos()

    # Normalizar columna estado
    if "estado" not in remolques.columns:
        remolques["estado"] = "disponible"
    else:
        remolques["estado"] = remolques["estado"].fillna("disponible").str.strip().str.lower()

    # Guardar posibles correcciones
    guardar_datos(remolques, mantenimientos)

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
            matricula = st.text_input("Introduce matrícula del remolque").strip().upper()
            tipo_mant = st.text_input("Descripción del mantenimiento")

            # Buscar subtipo automáticamente
            tipo_autom = subtipos[subtipos["matricula"] == matricula]["subtipo"]
            tipo_detectado = tipo_autom.iloc[0] if not tipo_autom.empty else ""
            st.info(f"Tipo detectado: **{tipo_detectado or 'No encontrado'}**")

            if st.button("Registrar entrada"):
                if matricula:
                    if matricula not in remolques["matricula"].values:
                        nuevo = pd.DataFrame([{
                            "matricula": matricula,
                            "tipo": tipo_detectado,
                            "parking": "",
                            "chofer": "",
                            "fecha": "",
                            "estado": "mantenimiento"
                        }])
                        remolques = pd.concat([remolques, nuevo], ignore_index=True)

                    if matricula not in mantenimientos["matricula"].values:
                        entrada = pd.DataFrame([{"matricula": matricula, "tipo_mantenimiento": tipo_mant}])
                        mantenimientos = pd.concat([mantenimientos, entrada], ignore_index=True)
                        remolques.loc[remolques["matricula"] == matricula, "estado"] = "mantenimiento"
                        if tipo_detectado:
                            remolques.loc[remolques["matricula"] == matricula, "tipo"] = tipo_detectado
                        guardar_datos(remolques, mantenimientos)
                        st.success(f"Remolque {matricula} registrado en mantenimiento.")
                    else:
                        st.warning("Ese remolque ya está registrado en mantenimiento.")
                else:
                    st.warning("Introduce una matrícula válida.")

        elif accion == "Fin de mantenimiento":
            if not mantenimientos.empty:
                matricula = st.selectbox("Selecciona matrícula en taller", mantenimientos["matricula"].unique())
                if st.button("Marcar como disponible"):
                    mantenimientos = mantenimientos[mantenimientos["matricula"] != matricula]
                    if matricula not in remolques["matricula"].values:
                        nuevo = pd.DataFrame([{
                            "matricula": matricula,
                            "tipo": "",
                            "parking": "",
                            "chofer": "",
                            "fecha": datetime.today().strftime('%Y-%m-%d'),
                            "estado": "disponible"
                        }])
                        remolques = pd.concat([remolques, nuevo], ignore_index=True)
                    else:
                        remolques.loc[remolques["matricula"] == matricula, "estado"] = "disponible"
                        remolques.loc[remolques["matricula"] == matricula, "fecha"] = datetime.today().strftime('%Y-%m-%d')
                    guardar_datos(remolques, mantenimientos)
                    st.success(f"Remolque {matricula} marcado como disponible.")
            else:
                st.info("No hay remolques en mantenimiento actualmente.")

        elif accion == "Asignación a chófer":
            disponibles = remolques[remolques["estado"] == "disponible"]
            if not disponibles.empty:
                matricula = st.selectbox("Selec
