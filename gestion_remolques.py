# gestion_remolques.py (Kanban + Auto eliminación + botón X + etiqueta días + jefe de tráfico)
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from io import BytesIO

DB_FILE = "remolques.db"

# ---------------------- UTILIDADES ----------------------
def cargar_tabla(nombre):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(f"SELECT * FROM {nombre}", conn)

def guardar_tabla(nombre, df):
    with sqlite3.connect(DB_FILE) as conn:
        df.to_sql(nombre, conn, index=False, if_exists="replace")

def registrar_movimiento(matricula, accion, tipo="", taller="", observaciones=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo = pd.DataFrame([{ 
        "fecha_hora": now,
        "matricula": matricula,
        "accion": accion,
        "tipo": tipo,
        "taller": taller,
        "observaciones": observaciones
    }])
    try:
        movimientos = cargar_tabla("movimientos")
        movimientos = pd.concat([movimientos, nuevo], ignore_index=True)
    except:
        movimientos = nuevo
    guardar_tabla("movimientos", movimientos)

# ---------------------- UI PRINCIPAL ----------------------
def gestion_remolques():
    def asegurar_tabla(nombre, columnas):
        try:
            df = cargar_tabla(nombre)
        except:
            df = pd.DataFrame(columns=columnas)
            guardar_tabla(nombre, df)

    asegurar_tabla("remolques", ["matricula", "tipo", "taller", "fecha", "parking", "estado", "observaciones"])
    asegurar_tabla("subtipos", ["matricula", "subtipo"])
    asegurar_tabla("movimientos", ["fecha_hora", "matricula", "accion", "tipo", "taller", "observaciones"])
    st.set_page_config(layout="wide")
    st.title("🚛 Gestión de Remolques ")

    remolques = cargar_tabla("remolques")
    subtipos = cargar_tabla("subtipos")

    columnas_necesarias = ["matricula", "tipo", "taller", "fecha", "parking", "estado", "observaciones"]
    for col in columnas_necesarias:
        if col not in remolques.columns:
            remolques[col] = ""
        remolques[col] = remolques[col].fillna("")

    remolques["estado"] = remolques["estado"].str.lower()

    filtro_matricula_global = st.text_input("🔎 Buscar matrícula", key="filtro_global").strip().upper()
    columnas = st.columns(3)
    estados = ["disponible", "mantenimiento", "asignado"]
    titulos = ["🟢 Disponibles", "🔧 En mantenimiento", "🚚 Asignados"]

    if "asignando" not in st.session_state:
        st.session_state.asignando = None
        st.session_state.chofer_inputs = {}
        st.session_state.jefe_inputs = {}
        st.session_state.observaciones_inputs = {}

    hoy = datetime.today()

    remolques_filtrados = []
    for _, row in remolques.iterrows():
        if row["estado"] == "asignado":
            try:
                fecha = datetime.strptime(row.get("fecha", ""), "%Y-%m-%d")
                if (hoy - fecha).days > 7:
                    continue
            except:
                pass
        remolques_filtrados.append(row)
    remolques = pd.DataFrame(remolques_filtrados)

    for col in columnas_necesarias:
        if col not in remolques.columns:
            remolques[col] = ""
        remolques[col] = remolques[col].fillna("")

    for idx, (col, estado, titulo) in enumerate(zip(columnas, estados, titulos)):
        with col:
            col.subheader(titulo)
        subdf = remolques[(remolques["estado"] == estado) & (remolques["matricula"].str.upper().str.contains(filtro_matricula_global))]
        for _, row in subdf.iterrows():
            if estado == "disponible":
                resumen = f"{row['matricula']} - {row.get('tipo', '')} - {row.get('parking', '')}"
            elif estado == "mantenimiento":
                resumen = f"{row['matricula']} - {row.get('taller', '')}"
            else:
                resumen = f"{row['matricula']} - {row.get('taller', '')}"
            with col.expander(resumen):
                st.markdown(f"**{row['matricula']}**  ")
                st.markdown(f"Tipo: {row.get('tipo', '')}  ")
                st.markdown(f"Taller: {row.get('taller', '-')}, Fecha: {row.get('fecha', '-')}")
                st.markdown(f"Parking: {row.get('parking', '-')}")
                if row.get("observaciones", ""):
                    st.markdown(f"📝 Observaciones: {row['observaciones']}")

                try:
                    fecha = datetime.strptime(row.get("fecha", ""), "%Y-%m-%d")
                    dias = (hoy - fecha).days
                    st.caption(f"🕒 Hace {dias} días")
                except:
                    pass

                if st.button("❌", key=f"borrar_{row['matricula']}"):
                    remolques = remolques[remolques["matricula"] != row["matricula"]]
                    registrar_movimiento(row['matricula'], "Borrado manual", row.get("tipo", ""))
                    guardar_tabla("remolques", remolques)
                    st.success(f"🗑 Remolque {row['matricula']} eliminado del panel")
                    st.stop()

                if estado == "disponible":
                    if st.session_state.asignando == row['matricula']:
                        st.session_state.chofer_inputs[row['matricula']] = st.text_input(f"Tractora para {row['matricula']}", key=f"input_{row['matricula']}")
                        st.session_state.jefe_inputs[row['matricula']] = st.text_input(f"Jefe de tráfico que asigna {row['matricula']}", key=f"jefe_{row['matricula']}")
                        st.session_state.observaciones_inputs[row['matricula']] = st.text_input(f"Observaciones para {row['matricula']}", key=f"obs_{row['matricula']}")
                        if st.button("Confirmar asignación", key=f"confirmar_{row['matricula']}"):
                            tractora = st.session_state.chofer_inputs[row['matricula']].strip()
                            jefe = st.session_state.jefe_inputs[row['matricula']].strip()
                            observaciones = st.session_state.observaciones_inputs[row['matricula']].strip()
                            if tractora and jefe:
                                remolques.loc[remolques['matricula'] == row['matricula'], ["estado", "taller", "fecha", "observaciones"]] = ["asignado", tractora, hoy.strftime("%Y-%m-%d"), observaciones]
                                registrar_movimiento(row['matricula'], "Asignado", row.get("tipo", ""), tractora, f"Asignado por {jefe}. {observaciones}")
                                guardar_tabla("remolques", remolques)
                                st.session_state.asignando = None
                                st.success(f"✅ {row['matricula']} asignado a {tractora} por {jefe}")
                                st.stop()
                            else:
                                st.warning("Debes introducir tanto la tractora como el nombre del jefe de tráfico.")
                        if st.button("Cancelar", key=f"cancelar_{row['matricula']}"):
                            st.session_state.asignando = None
                    else:
                        if st.button(f"Asignar {row['matricula']}", key=f"asignar_{row['matricula']}"):
                            st.session_state.asignando = row['matricula']

                elif estado == "asignado":
                    if st.button(f"Finalizar {row['matricula']}", key=f"finalizar_{row['matricula']}"):
                        remolques.loc[remolques['matricula'] == row['matricula'], ["estado", "taller"]] = ["disponible", ""]
                        registrar_movimiento(row['matricula'], "Finalización de uso", row.get("tipo", ""), row.get("taller", ""))
                        guardar_tabla("remolques", remolques)
                        st.success(f"✅ {row['matricula']} marcado como disponible")
                        st.stop()

                elif estado == "mantenimiento":
                    parking_reparado = st.text_input(f"Parking donde queda {row['matricula']}", key=f"parking_{row['matricula']}")
                    if st.button(f"Reparado {row['matricula']}", key=f"reparado_{row['matricula']}"):
                        if parking_reparado.strip():
                            remolques.loc[remolques['matricula'] == row['matricula'], ["estado", "parking"]] = ["disponible", parking_reparado.strip()]
                            registrar_movimiento(row['matricula'], "Fin mantenimiento", row.get("tipo", ""), observaciones=f"Queda en {parking_reparado.strip()}")
                            guardar_tabla("remolques", remolques)
                            st.success(f"🔧 {row['matricula']} reparado y ubicado en {parking_reparado.strip()}")
                            st.stop()
                        else:
                            st.warning("Debes indicar el parking donde queda el remolque.")
