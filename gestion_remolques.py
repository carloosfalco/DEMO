# gestion_remolques.py (rediseñado en modo Kanban)
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO

DB_FILE = "remolques.db"

# ---------------------- UTILIDADES ----------------------
def cargar_tabla(nombre):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(f"SELECT * FROM {nombre}", conn)

def guardar_tabla(nombre, df):
    with sqlite3.connect(DB_FILE) as conn:
        df.to_sql(nombre, conn, index=False, if_exists="replace")

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
        movimientos = cargar_tabla("movimientos")
        movimientos = pd.concat([movimientos, nuevo], ignore_index=True)
    except:
        movimientos = nuevo
    guardar_tabla("movimientos", movimientos)

# ---------------------- UI PRINCIPAL ----------------------
def gestion_remolques():
    st.set_page_config(layout="wide")
    st.title("🚛 Gestión Visual de Remolques (Kanban)")

    remolques = cargar_tabla("remolques")
    subtipos = cargar_tabla("subtipos")

    remolques["estado"] = remolques["estado"].fillna("disponible").str.lower()
    columnas = st.columns(3)

    estados = ["disponible", "mantenimiento", "asignado"]
    titulos = ["🟢 Disponibles", "🛠 En mantenimiento", "🚚 Asignados"]

    for col, estado, titulo in zip(columnas, estados, titulos):
        col.subheader(titulo)
        subdf = remolques[remolques["estado"] == estado]
        for _, row in subdf.iterrows():
            with col.container():
                st.markdown(f"**{row['matricula']}**  ")
                st.markdown(f"Tipo: {row.get('tipo', '')}  ")
                st.markdown(f"Chofer: {row.get('chofer', '-')}, Fecha: {row.get('fecha', '-')}")
                st.markdown(f"Parking: {row.get('parking', '-')}")

                if estado == "disponible":
                    if st.button(f"Asignar {row['matricula']}", key=f"asignar_{row['matricula']}"):
                        chofer = st.text_input(f"Chofer para {row['matricula']}", key=f"chofer_{row['matricula']}")
                        if chofer:
                            remolques.loc[remolques['matricula'] == row['matricula'], ["estado", "chofer", "fecha"]] = ["asignado", chofer, datetime.today().strftime("%Y-%m-%d")]
                            registrar_movimiento(row['matricula'], "Asignado", row.get("tipo", ""), chofer)
                            guardar_tabla("remolques", remolques)
                            st.experimental_rerun()
                elif estado == "asignado":
                    if st.button(f"Finalizar {row['matricula']}", key=f"finalizar_{row['matricula']}"):
                        remolques.loc[remolques['matricula'] == row['matricula'], ["estado", "chofer"]] = ["disponible", ""]
                        registrar_movimiento(row['matricula'], "Finalización de uso", row.get("tipo", ""), row.get("chofer", ""))
                        guardar_tabla("remolques", remolques)
                        st.experimental_rerun()
                elif estado == "mantenimiento":
                    if st.button(f"Reparado {row['matricula']}", key=f"reparado_{row['matricula']}"):
                        remolques.loc[remolques['matricula'] == row['matricula'], ["estado"]] = ["disponible"]
                        registrar_movimiento(row['matricula'], "Fin mantenimiento", row.get("tipo", ""))
                        guardar_tabla("remolques", remolques)
                        st.experimental_rerun()

    st.divider()

    with st.expander("➕ Registrar nuevo movimiento", expanded=False):
        matricula = st.text_input("Matrícula").strip().upper()
        tipo_detectado = subtipos[subtipos["matricula"].str.strip().str.upper() == matricula]["subtipo"].values
        tipo = tipo_detectado[0] if len(tipo_detectado) > 0 else st.text_input("Tipo de vehículo")
        mantenimiento = st.text_input("Descripción del mantenimiento")
        fecha = st.date_input("Última fecha de uso")
        chofer = st.text_input("Último chófer")

        if st.button("Registrar en mantenimiento"):
            nuevo = pd.DataFrame([{ "matricula": matricula, "tipo": tipo, "chofer": chofer, "fecha": fecha.strftime('%Y-%m-%d'), "parking": "", "estado": "mantenimiento" }])
            if matricula in remolques["matricula"].values:
                remolques = remolques[remolques["matricula"] != matricula]
            remolques = pd.concat([remolques, nuevo], ignore_index=True)
            registrar_movimiento(matricula, "Entrada a mantenimiento", tipo, chofer, mantenimiento)
            guardar_tabla("remolques", remolques)
            st.success(f"Remolque {matricula} registrado en mantenimiento.")
            st.experimental_rerun()

    st.divider()
    with st.expander("📁 Exportar historial"):
        movimientos = cargar_tabla("movimientos")
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            movimientos.to_excel(writer, index=False, sheet_name="Historial")
        output.seek(0)
        st.download_button("📄 Descargar historial", data=output, file_name="historial_remolques.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
