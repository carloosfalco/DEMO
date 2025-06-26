# gestion_remolques.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os

REMOLQUES_FILE = "remolques.csv"
MANTENIMIENTOS_FILE = "mantenimientos.csv"
SUBTIPOS_FILE = "subtipos_remolques.csv"
MOVIMIENTOS_FILE = "movimientos_remolques.csv"

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

def registrar_movimiento(matricula, accion, tipo="", chofer="", observaciones=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo = pd.DataFrame([{ 
        "fecha_hora": now,
        "matricula": matricula,
        "accion": accion,
        "tipo": tipo,
        "chofer": chofer,
        "observaciones": observaciones
    }])
    try:
        movimientos = pd.read_csv(MOVIMIENTOS_FILE)
        movimientos = pd.concat([movimientos, nuevo], ignore_index=True)
    except FileNotFoundError:
        movimientos = nuevo
    movimientos.to_csv(MOVIMIENTOS_FILE, index=False)

def gestion_remolques():
    st.title("🛠 Gestión de Remolques")
    remolques, mantenimientos, subtipos = cargar_datos()

    if "estado" not in remolques.columns:
        remolques["estado"] = "disponible"
    else:
        remolques["estado"] = remolques["estado"].fillna("disponible").str.strip().str.lower()

    guardar_datos(remolques, mantenimientos)

    tab1, tab2, tab3 = st.tabs(["📋 Disponibles", "🛻 En mantenimiento", "➕ Registrar movimiento"])

    with tab1:
        st.subheader("Remolques disponibles")
        disponibles = remolques[remolques["estado"] == "disponible"].copy()

        if not disponibles.empty:
            disponibles["fecha"] = pd.to_datetime(disponibles["fecha"], errors="coerce")
            disponibles = disponibles[["matricula", "tipo", "chofer", "fecha", "parking"]]
            disponibles.columns = ["Matrícula", "Tipo", "Último chófer", "Última fecha de uso", "Parking"]
            disponibles_filtrados = disponibles.copy()

            with st.expander("🔎 Filtros avanzados", expanded=False):
                tipo_filtro = st.multiselect("Filtrar por tipo", disponibles["Tipo"].dropna().unique())
                chofer_filtro = st.multiselect("Filtrar por chófer", disponibles["Último chófer"].dropna().unique())
                parking_filtro = st.multiselect("Filtrar por parking", disponibles["Parking"].dropna().unique())

                min_fecha = disponibles["Última fecha de uso"].min()
                max_fecha = disponibles["Última fecha de uso"].max()
                activar_fecha = st.checkbox("Filtrar por fecha de uso")
                if activar_fecha:
                    fecha_rango = st.date_input("Rango de fechas", value=(min_fecha, max_fecha))

            if tipo_filtro:
                disponibles_filtrados = disponibles_filtrados[disponibles_filtrados["Tipo"].isin(tipo_filtro)]
            if chofer_filtro:
                disponibles_filtrados = disponibles_filtrados[disponibles_filtrados["Último chófer"].isin(chofer_filtro)]
            if parking_filtro:
                disponibles_filtrados = disponibles_filtrados[disponibles_filtrados["Parking"].isin(parking_filtro)]
            if activar_fecha:
                fmin, fmax = fecha_rango
                disponibles_filtrados = disponibles_filtrados[(disponibles_filtrados["Última fecha de uso"] >= pd.to_datetime(fmin)) & (disponibles_filtrados["Última fecha de uso"] <= pd.to_datetime(fmax))]

            disponibles_filtrados = disponibles_filtrados.sort_values("Última fecha de uso", ascending=False)
            st.dataframe(disponibles_filtrados, use_container_width=True)
        else:
            st.info("No hay remolques disponibles actualmente.")

    with tab2:
        st.subheader("Remolques en mantenimiento")
        st.dataframe(mantenimientos)

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
                        nuevo = pd.DataFrame([{ "matricula": matricula, "tipo": tipo, "parking": "", "chofer": ultimo_chofer, "fecha": ultima_fecha.strftime('%Y-%m-%d'), "estado": "mantenimiento" }])
                        remolques = pd.concat([remolques, nuevo], ignore_index=True)
                    else:
                        remolques.loc[remolques["matricula"].str.upper() == matricula, ["tipo", "chofer", "fecha", "estado"]] = tipo, ultimo_chofer, ultima_fecha.strftime('%Y-%m-%d'), "mantenimiento"
                    if matricula not in mantenimientos["matricula"].values:
                        entrada = pd.DataFrame([{ "matricula": matricula, "tipo_mantenimiento": tipo_mant }])
                        mantenimientos = pd.concat([mantenimientos, entrada], ignore_index=True)
                    registrar_movimiento(matricula, "Entrada a mantenimiento", tipo, ultimo_chofer, tipo_mant)
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
                        nuevo = pd.DataFrame([{ "matricula": matricula, "tipo": "", "parking": "", "chofer": "", "fecha": datetime.today().strftime('%Y-%m-%d'), "estado": "disponible" }])
                        remolques = pd.concat([remolques, nuevo], ignore_index=True)
                    else:
                        remolques.loc[remolques["matricula"] == matricula, ["estado", "fecha"]] = "disponible", datetime.today().strftime('%Y-%m-%d')
                    registrar_movimiento(matricula, "Fin de mantenimiento")
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
                    remolques.loc[remolques["matricula"] == matricula, ["estado", "chofer", "fecha"]] = "asignado", chofer, datetime.today().strftime('%Y-%m-%d')
                    registrar_movimiento(matricula, "Asignación a chófer", chofer=chofer)
                    guardar_datos(remolques, mantenimientos)
                    st.success(f"Remolque {matricula} asignado a {chofer}.")
            else:
                st.info("No hay remolques disponibles.")

        st.divider()

        if not os.path.exists(MOVIMIENTOS_FILE):
            pd.DataFrame(columns=["fecha_hora", "matricula", "accion", "tipo", "chofer", "observaciones"]).to_csv(MOVIMIENTOS_FILE, index=False)

        with open(MOVIMIENTOS_FILE, "rb") as f:
            st.download_button("📃 Exportar historial de movimientos", data=f, file_name="historial_movimientos.csv")
