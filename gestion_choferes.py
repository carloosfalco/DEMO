# gestion_choferes.py

import streamlit as st
from pyairtable import Table
from pyairtable.formulas import match

def gestion_choferes():
    st.title("🚚 Gestión de Chóferes – Fleet and Route Management")

    # --- Configuración segura ---
    AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
    BASE_ID = "appxhB5R5nco0MZpT"
    TABLE_NAME = "Fleet and Route Management"

    # --- Conexión a Airtable ---
    table = Table(AIRTABLE_TOKEN, BASE_ID, TABLE_NAME)

    # --- Buscador por nombre ---
    search_name = st.text_input("🔍 Buscar por nombre de chófer:")

    if search_name:
        formula = match({"Chofer": search_name})
        records = table.all(formula=formula)
    else:
    try:
        records = table.all()
        st.success(f"✅ Se han recibido {len(records)} registros.")
    except Exception as e:
        st.error("❌ Error al obtener los registros de Airtable.")
        st.exception(e)
        return


    # --- Mostrar resultados ---
    if not records:
        st.warning("No se encontraron registros.")
    else:
        for record in records:
            record_id = record["id"]
            data = record.get("fields", {})

            st.markdown("---")
            st.subheader(f"👤 {data.get('Chofer', 'Sin nombre')}")

            tractora = st.text_input("🚛 Matrícula tractora", value=data.get("Matr Tractora", ""), key=f"tractora_{record_id}")
            remolque = st.text_input("🛻 Matrícula remolque", value=data.get("Matr Remolque", ""), key=f"remolque_{record_id}")
            estado = st.text_input("📍 Estado", value=data.get("ESTADO", ""), key=f"estado_{record_id}")

            if st.button("💾 Guardar cambios", key=f"guardar_{record_id}"):
                updates = {
                    "Matr Tractora": tractora,
                    "Matr Remolque": remolque,
                    "ESTADO": estado
                }
                table.update(record_id, updates)
                st.success("✅ Registro actualizado correctamente.")
