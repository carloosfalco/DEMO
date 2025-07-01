import streamlit as st
from rutas import planificador_rutas
from orden_carga_generator_manual import generar_orden_carga_manual
from gestion_remolques import gestion_remolques
from consulta_matriculas import consulta_matriculas
from gestion_choferes import gestion_choferes  # 👈 NUEVO

def main():
    st.set_page_config(page_title="Virosque TMS", page_icon="🚛", layout="wide")

    st.sidebar.title("📂 Menú")
    seleccion = st.sidebar.radio("Selecciona una opción", [
        "Planificador de rutas",
        "Orden de carga",
        "Gestión de remolques",
        "Consulta de matrículas",
        "Gestión de chóferes"  # 👈 NUEVA OPCIÓN
    ])

    if seleccion == "Planificador de rutas":
        planificador_rutas()
    elif seleccion == "Orden de carga":
        generar_orden_carga_manual()
    elif seleccion == "Gestión de remolques":
        gestion_remolques()
    elif seleccion == "Consulta de matrículas":
        consulta_matriculas()
    elif seleccion == "Gestión de chóferes":
        gestion_choferes()  # 👈 NUEVO ENLACE

if __name__ == "__main__":
    main()
