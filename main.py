import streamlit as st
from rutas import planificador_rutas
from orden_carga_generator_manual import generar_orden_carga_manual

def main():
    st.set_page_config(page_title="Virosque TMS", page_icon="🚛", layout="wide")

    st.sidebar.title("📂 Menú")

    # Si se ha pulsado "Nueva orden de carga", limpiar y redirigir
    if st.sidebar.button("🧹 Nueva orden de carga"):
        st.query_params.clear()
        st.query_params["nueva_orden"] = "1"
        st.query_params["seleccion"] = "Orden de carga"
        st.rerun()

    # Selección de menú
    seleccion = st.sidebar.radio(
        "Selecciona una opción",
        ["Planificador de rutas", "Orden de carga"],
        index=1 if st.query_params.get("seleccion") == "Orden de carga" else 0
    )

    # Ejecutar la sección correspondiente
    if seleccion == "Planificador de rutas":
        planificador_rutas()
    elif seleccion == "Orden de carga":
        generar_orden_carga_manual()

if __name__ == "__main__":
    main()
