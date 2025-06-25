import streamlit as st
from rutas import planificador_rutas
from orden_carga_generator_manual import generar_orden_carga_manual


def main():
    st.set_page_config(page_title="Virosque TMS", page_icon="🚛", layout="wide")

    st.sidebar.title("📂 Menú")
    
    # Botón de reinicio para nueva orden de carga
    if st.sidebar.button("🧹 Nueva orden de carga"):
        st.query_params["nueva_orden"] = "1"
        st.rerun()

    seleccion = st.sidebar.radio("Selecciona una opción", [
        "Planificador de rutas",
        "Orden de carga"
    ])

    if seleccion == "Planificador de rutas":
        planificador_rutas()

    elif seleccion == "Orden de carga":
        generar_orden_carga_manual()


if __name__ == "__main__":
    main()
