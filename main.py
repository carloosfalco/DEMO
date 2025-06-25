import streamlit as st
from rutas import planificador_rutas
from orden_carga_generator_manual import generar_orden_carga_manual

def main():
    st.set_page_config(page_title="Virosque TMS", page_icon="🚛", layout="wide")

    st.sidebar.title("📂 Menú")

    # Inicializar variable de selección en sesión
    if "seleccion" not in st.session_state:
        st.session_state["seleccion"] = "Planificador de rutas"

    # Botón para limpiar y saltar a orden de carga
    if st.sidebar.button("🧹 Nueva orden de carga"):
        st.session_state.clear()
        st.session_state["nueva_orden"] = True
        st.session_state["seleccion"] = "Orden de carga"
        st.rerun()

    # Selector de menú (controlado por session_state)
    seleccion = st.sidebar.radio(
        "Selecciona una opción",
        ["Planificador de rutas", "Orden de carga"],
        index=0 if st.session_state["seleccion"] == "Planificador de rutas" else 1,
        key="seleccion"
    )

    # Mostrar la página adecuada
    if seleccion == "Planificador de rutas":
        planificador_rutas()
    elif seleccion == "Orden de carga":
        generar_orden_carga_manual()

if __name__ == "__main__":
    main()
