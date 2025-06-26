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

    # Normalizar estado
    if "estado" not in remolques.columns:
        remolques["estado"] = "disponible"
    else:
        remolques["estado"] = remolques["estado"].fillna("disponible").str.strip().str.lower()

    guardar_datos(remolques, mantenimientos)

    tab1, tab2, tab3 = st.tabs(["📋 Disponibles", "🧰 En mantenimiento", "➕ Registrar movimiento"])

    # ✅ TABLA FILTRABLE DE DISPONIBLES
    with tab1:
        st.subheader("Remolques disponibles")

        disponibles = remolques[remolques["estado"] == "disponible"].copy()

        if not disponibles.empty:
            disponibles["fecha"] = pd.to_datetime(disponibles["fecha"], errors="coerce")
            disponibles = disponibles[["matricula", "tipo", "chofer", "fecha", "parking"]]
            disponibles.columns = ["Matrícula", "Tipo", "Último chófer", "Última fecha de uso", "Parking"]

            with st.expander("🔎 Filtros avanzados", expanded=True):
                tipo_filtro = st.multiselect("Filtrar por tipo", disponibles["Tipo"].dropna().unique())
                chofer_filtro = st.multiselect("Filtrar por chófer", disponibles["Último chófer"].dropna().unique())
                parking_filtro = st.multiselect("Filtrar por parking", disponibles["Parking"].dropna().unique())
                fecha_min = disponibles["Última fecha de uso"].min()
                fecha_max = disponibles["Última fecha de uso"].max()
                fecha_rango = st.date_input("Filtrar por fecha de uso", value=(fecha_min, fecha_max))

            if tipo_filtro:
                disponibles = disponibles[disponibles["Tipo"].isin(tipo_filtro)]
            if chofer_filtro:
                disponibles = disponibles[disponibles["Último chófer"].isin(chofer_filtro)]
            if parking_filtro:
                disponibles = disponibles[disponibles["Parking"].isin(parking_filtro)]
            if fecha_rango:
                fmin, fmax = fecha_rango
                disponibles = disponibles[
                    (disponibles["Última fecha de uso"] >= pd.to_datetime(fmin)) &
                    (disponibles["Última fecha de uso"] <= pd.to_datetime(fmax))
                ]

            disponibles = disponibles.sort_values("Última fecha de uso", ascending=False)
            st.dataframe(disponibles, use_container_width=True)
        else:
            st.info("No hay remolques disponibles actualmente.")

    # ✅ TABLA DE REMOLQUES EN MANTENIMIENTO
    with tab2:
        st.subheader("Remolques en mantenimiento")
        st.dataframe(mantenimientos)

    # ✅ FORMULARIO DE ENTRADA, SALIDA Y ASIGNACIÓN
    with tab3:
        st.subheader("Registrar entrada o salida")
        accion = st.radio("¿Qué quieres registrar?", ["Entrada a mantenimiento", "Fin de mantenimiento", "Asignación a chófer"])

        if accion == "Entrada a mantenimiento":
            matricula = st.text_input("Introduce matrícula del remolque").strip().upper()
            subtipos["matricula"] = subtipos["matricula"].astype(str).str.strip().str.upper()
            tipo_detectado = subtipos[subtipos["matricula"] == matricula]["subtipo"]
            tipo_default = tipo_detectado.iloc[0] if not tipo_detectado.empty else ""
            tipo = st.text_input("Tipo de vehículo", value=tipo_default)
            tipo_mant = st.text_input("Descripción del mantenimiento")
            ultima_fecha = st.date_input("Última fecha de uso")
            ultimo_chofer = st.text_input("Último chófer")

            if st.button("Registrar entrada"):
                if matricula and tipo_mant:
                    ya_existe = remolques["matricula"].str.upper().eq(matricula).any()

                    if not ya_existe:
                        nuevo = pd.DataFrame([{
                            "matricula": matricula,
                            "tipo": tipo,
                            "parking": "",
                            "chofer": ultimo_chofer,
                            "fecha": ultima_fecha.strftime('%Y-%m-%d'),
                            "estado": "mantenimiento"
                        }])
                        remolques = pd.concat([remolques, nuevo], ignore_index=True)
                    else:
                        remolques.loc[remolques["matricula"].str.upper() == matricula, "tipo"] = tipo
                        remolques.loc[remolques["matricula"].str.upper() == matricula, "chofer"] = ultimo_chofer
                        remolques.loc[remolques["matricula"].str.upper() == matricula, "fecha"] = ultima_fecha.strftime('%Y-%m-%d')
                        remolques.loc[remolques["matricula"].str.upper() == matricula, "estado"] = "mantenimiento"

                    if matricula not in mantenimientos["matricula"].values:
                        entrada = pd.DataFrame([{"matricula": matricula, "tipo_mantenimiento": tipo_mant}])
                        mantenimientos = pd.concat([mantenimientos, entrada], ignore_index=True)

                    guardar_datos(remolques, mantenimientos)
                    st.success(f"Remolque {matricula} registrado en mantenimiento.")
                else:
                    st.warning("Debes introducir matrícula y descripción del mantenimiento.")

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
                matricula = st.selectbox("Selecciona matrícula disponible", disponibles["matricula"])
                chofer = st.text_input("Nombre del chófer")
                if st.button("Asignar remolque"):
                    remolques.loc[remolques["matricula"] == matricula, "estado"] = "asignado"
                    remolques.loc[remolques["matricula"] == matricula, "chofer"] = chofer
                    remolques.loc[remolques["matricula"] == matricula, "fecha"] = datetime.today().strftime('%Y-%m-%d')
                    guardar_datos(remolques, mantenimientos)
                    st.success(f"Remolque {matricula} asignado a {chofer}.")
            else:
                st.info("No hay remolques disponibles.")
