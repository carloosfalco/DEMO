# gestion_remolques.py con base de datos SQLite
import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
from io import BytesIO
import os

DB_FILE = "remolques.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS remolques (
                        matricula TEXT PRIMARY KEY,
                        tipo TEXT,
                        parking TEXT,
                        chofer TEXT,
                        fecha TEXT,
                        estado TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS mantenimientos (
                        matricula TEXT PRIMARY KEY,
                        tipo_mantenimiento TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS movimientos (
                        fecha_hora TEXT,
                        matricula TEXT,
                        accion TEXT,
                        tipo TEXT,
                        chofer TEXT,
                        observaciones TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS subtipos (
                        matricula TEXT PRIMARY KEY,
                        subtipo TEXT
                    )''')
        conn.commit()

def cargar_df(query):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(query, conn)

def ejecutar(query, params=()):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(query, params)
        conn.commit()

def registrar_movimiento(matricula, accion, tipo="", chofer="", observaciones=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ejecutar("INSERT INTO movimientos VALUES (?, ?, ?, ?, ?, ?)", (now, matricula, accion, tipo, chofer, observaciones))

def guardar_remolque(matricula, tipo, parking, chofer, fecha, estado):
    ejecutar("REPLACE INTO remolques VALUES (?, ?, ?, ?, ?, ?)", (matricula, tipo, parking, chofer, fecha, estado))

def gestion_remolques():
    st.title("🛠 Gestión de Remolques")
    init_db()

    remolques = cargar_df("SELECT * FROM remolques")
    mantenimientos = cargar_df("SELECT * FROM mantenimientos")
    subtipos = cargar_df("SELECT * FROM subtipos")

    tab1, tab2, tab3 = st.tabs(["📋 Disponibles", "🛻 En mantenimiento", "➕ Registrar movimiento"])

    with tab1:
        st.subheader("Remolques disponibles")
        disponibles = remolques[remolques["estado"].str.lower() == "disponible"]

        if not disponibles.empty:
            disponibles["fecha"] = pd.to_datetime(disponibles["fecha"], errors="coerce")
            disponibles = disponibles[["matricula", "tipo", "chofer", "fecha", "parking"]]
            disponibles.columns = ["Matrícula", "Tipo", "Último chófer", "Última fecha de uso", "Parking"]
            disponibles_filtrados = disponibles.copy()

            with st.expander("🔎 Filtros avanzados", expanded=False):
                tipo_filtro = st.multiselect("Filtrar por tipo", disponibles["Tipo"].dropna().unique())
                chofer_filtro = st.multiselect("Filtrar por chófer", disponibles["Último chófer"].dropna().unique())
                parking_filtro = st.multiselect("Filtrar por parking", disponibles["Parking"].dropna().unique())

                activar_fecha = st.checkbox("Filtrar por fecha de uso")
                if activar_fecha:
                    min_fecha = disponibles["Última fecha de uso"].min()
                    max_fecha = disponibles["Última fecha de uso"].max()
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
                    ejecutar("REPLACE INTO mantenimientos VALUES (?, ?)", (matricula, tipo_mant))
                    guardar_remolque(matricula, tipo, "", ultimo_chofer, ultima_fecha.strftime('%Y-%m-%d'), "mantenimiento")
                    registrar_movimiento(matricula, "Entrada a mantenimiento", tipo, ultimo_chofer, tipo_mant)
                    st.success(f"Remolque {matricula} registrado en mantenimiento.")
                else:
                    st.warning("Debes introducir matrícula y descripción del mantenimiento.")

        elif accion == "Fin de mantenimiento":
            matriculas = mantenimientos["matricula"].tolist()
            if matriculas:
                matricula = st.selectbox("Selecciona matrícula en taller", matriculas)
                if st.button("Marcar como disponible"):
                    ejecutar("DELETE FROM mantenimientos WHERE matricula = ?", (matricula,))
                    guardar_remolque(matricula, remolques[remolques.matricula == matricula]["tipo"].values[0] if matricula in remolques.matricula.values else "", "", "", datetime.today().strftime('%Y-%m-%d'), "disponible")
                    registrar_movimiento(matricula, "Fin de mantenimiento")
                    st.success(f"Remolque {matricula} marcado como disponible.")
            else:
                st.info("No hay remolques en mantenimiento actualmente.")

        elif accion == "Asignación a chófer":
            disponibles = remolques[remolques["estado"] == "disponible"]
            if not disponibles.empty:
                matricula = st.selectbox("Selecciona matrícula disponible", disponibles["matricula"])
                chofer = st.text_input("Nombre del chófer")
                if st.button("Asignar remolque"):
                    ejecutar("UPDATE remolques SET estado = ?, chofer = ?, fecha = ? WHERE matricula = ?", ("asignado", chofer, datetime.today().strftime('%Y-%m-%d'), matricula))
                    registrar_movimiento(matricula, "Asignación a chófer", chofer=chofer)
                    st.success(f"Remolque {matricula} asignado a {chofer}.")
            else:
                st.info("No hay remolques disponibles.")

        st.divider()

        movimientos_df = cargar_df("SELECT * FROM movimientos")
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            movimientos_df.to_excel(writer, index=False, sheet_name="Historial")
        output.seek(0)

        st.download_button(
            "📃 Exportar historial de movimientos",
            data=output,
            file_name="historial_movimientos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
