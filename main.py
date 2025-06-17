import streamlit as st
from rutas import planificador_rutas
from orden_carga_generator import generar_instrucciones_ruta
from orden_carga_generator_manual import generar_orden_carga_manual


def main():
    st.set_page_config(page_title="Virosque TMS", page_icon="🚛", layout="wide")

    st.sidebar.title("📂 Menú")
    seleccion = st.sidebar.radio("Selecciona una opción", [
        "Planificador de rutas",
        "Orden de carga (Excel)",
        "Orden de carga (Manual)"
    ])

    if seleccion == "Planificador de rutas":
        planificador_rutas()
    elif seleccion == "Orden de carga (Excel)":
        generar_instrucciones_ruta()
    elif seleccion == "Orden de carga (Manual)":
        generar_orden_carga_manual()

if __name__ == "__main__":
    main()

