import streamlit as st
from rutas import planificador_rutas
from orden_carga_generator_manual import generar_orden_carga_manual

def main():
    st.set_page_config(page_title="Virosque TMS", page_icon="🚛", layout="wide")

    st.sidebar.title("📂 Menú")

    # Manejo del botón que inicia una nueva orden y cambia la vista
    if st.sidebar.button("🧹 Nueva orden de carga"):
        st.query_params.clear()
        st.query_params.update({"nueva_orden": "1", "vista": "Orden de carga"})
        st.rerun()

    # Leer desde query_params si se ha pulsado el botón
    seleccion = st.query_params.get("vista", "Planificador de rutas")

    seleccion = st.sidebar.radio("Selecciona una opción", [
        "Planificador de rutas",
        "Orden de carga"
    ], index=1 if seleccion == "Orden de carga" else 0)

    # Actualiza la vista activa en query_params para persistencia
    st.query_params["vista"] = seleccion

    if seleccion == "Planificador de rutas":
        planificador_rutas()
    elif seleccion == "Orden de carga":
        generar_orden_carga_manual()

if __name__ == "__main__":
    main()
