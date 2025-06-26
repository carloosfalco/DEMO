import streamlit as st
from rutas import planificador_rutas
from orden_carga_generator_manual import generar_orden_carga_manual
from gestion_remolques import gestion_remolques  # 👈 NUEVO

def main():
    st.set_page_config(page_title="Virosque TMS", page_icon="🚛", layout="wide")

    st.sidebar.title("📂 Menú")
    seleccion = st.sidebar.radio("Selecciona una opción", [
        "Planificador de rutas",
        "Orden de carga",
        "Gestión de remolques"  # 👈 NUEVA OPCIÓN
    ])

    if seleccion == "Planificador de rutas":
        planificador_rutas()
    elif seleccion == "Orden de carga":
        generar_orden_carga_manual()
    elif seleccion == "Gestión de remolques":
        gestion_remolques()  # 👈 FUNCIÓN NUEVA

if __name__ == "__main__":
    main()
