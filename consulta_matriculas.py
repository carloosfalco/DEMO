import streamlit as st
import pandas as pd
from datetime import datetime

def consulta_matriculas():
    st.title("🔍 Consulta de matrículas")

    @st.cache_data
    def load_data():
        choferes = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Chóferes")
        remolques = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Remolques")
        tractoras = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Tractoras")
        return choferes, remolques, tractoras

    choferes_df, remolques_df, tractoras_df = load_data()

    matricula_input = st.text_input("Introduce una matrícula de tractora o remolque:").upper().strip()

    if matricula_input:
        # Buscar si es tractora
        tractora_row = tractoras_df[tractoras_df["Matrícula"] == matricula_input]
        if not tractora_row.empty:
            chofer = tractora_row.iloc[0]["Chofer asignado"]
            remolque = tractora_row.iloc[0]["Remolque asignado"]
            jefe = choferes_df[choferes_df["Chofer"] == chofer]["Jefe de tráfico"].values[0] if chofer in choferes_df["Chofer"].values else "Desconocido"
            st.success(f"La tractora {matricula_input} la conduce {chofer} junto al remolque {remolque} y su jefe de tráfico es {jefe}.")

        else:
            # Buscar si es remolque
            remolque_row = remolques_df[remolques_df["Matrícula"] == matricula_input]
            if not remolque_row.empty:
                chofer = remolque_row.iloc[0]["Chofer asignado"]
                tractora = remolque_row.iloc[0]["Tractora asignada"]
                jefe = choferes_df[choferes_df["Chofer"] == chofer]["Jefe de tráfico"].values[0] if chofer in choferes_df["Chofer"].values else "Desconocido"
                st.success(f"El remolque {matricula_input} está asignado a {chofer}, que conduce la tractora {tractora} bajo la supervisión de {jefe}.")
            else:
                st.error("Matrícula no encontrada en el sistema.")

    st.divider()
    st.title("🔁 Registro de cambios de asignación")

    st.subheader("Formulario de cambio")
    chofer = st.selectbox("Chofer que realiza el cambio:", choferes_df["Chofer"].unique())
    remolque_actual = st.text_input("Remolque que deja (si aplica):").upper().strip()
    estado_remolque = st.selectbox("Nuevo estado del remolque dejado:", ["Disponible", "Mantenimiento", "Baja", ""])
    remolque_nuevo = st.text_input("Nuevo remolque que asume (si aplica):").upper().strip()
    tractora_actual = choferes_df[choferes_df["Chofer"] == chofer]["Tractora asignada"].values[0]
    tractora_nueva = st.text_input("Nueva tractora que asume (si aplica, dejar vacío si se queda sin tractora):").upper().strip()

    confirmar = st.button("Registrar cambio")

    if confirmar:
        # Actualizar en Choferes
        choferes_df.loc[choferes_df["Chofer"] == chofer, "Remolque asignado"] = remolque_nuevo
        choferes_df.loc[choferes_df["Chofer"] == chofer, "Tractora asignada"] = tractora_nueva

        # Actualizar en Remolques: el anterior
        if remolque_actual in remolques_df["Matrícula"].values:
            remolques_df.loc[remolques_df["Matrícula"] == remolque_actual, "Estado"] = estado_remolque
            remolques_df.loc[remolques_df["Matrícula"] == remolque_actual, ["Chofer asignado", "Tractora asignada"]] = ["", ""]

        # Actualizar en Remolques: el nuevo
        if remolque_nuevo in remolques_df["Matrícula"].values:
            remolques_df.loc[remolques_df["Matrícula"] == remolque_nuevo, "Chofer asignado"] = chofer
            remolques_df.loc[remolques_df["Matrícula"] == remolque_nuevo, "Tractora asignada"] = tractora_nueva

        # Desvincular tractora anterior si cambia o se queda sin tractora
        if tractora_actual:
            tractoras_df.loc[tractoras_df["Matrícula"] == tractora_actual, ["Remolque asignado", "Chofer asignado"]] = ["", ""]

        # Asignar nueva tractora si hay
        if tractora_nueva:
            tractoras_df.loc[tractoras_df["Matrícula"] == tractora_nueva, "Remolque asignado"] = remolque_nuevo
            tractoras_df.loc[tractoras_df["Matrícula"] == tractora_nueva, "Chofer asignado"] = chofer

        # Guardar los cambios en Excel
        with pd.ExcelWriter("base_datos_MAKE_Virosque.xlsx", engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
            choferes_df.to_excel(writer, sheet_name="Chóferes", index=False)
            remolques_df.to_excel(writer, sheet_name="Remolques", index=False)
            tractoras_df.to_excel(writer, sheet_name="Tractoras", index=False)

        # Registrar en historial
        try:
            historial_df = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Historial")
        except:
            historial_df = pd.DataFrame(columns=["Fecha", "Evento"])

        evento = f"{chofer} deja remolque {remolque_actual} (→ {estado_remolque}), asume remolque {remolque_nuevo} y tractora {tractora_nueva or 'ninguna'}"
        nueva_fila = pd.DataFrame({"Fecha": [datetime.now()], "Evento": [evento]})
        historial_df = pd.concat([historial_df, nueva_fila], ignore_index=True)

        with pd.ExcelWriter("base_datos_MAKE_Virosque.xlsx", engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
            historial_df.to_excel(writer, sheet_name="Historial", index=False)

        st.success("✅ Cambio registrado y guardado correctamente.")

    st.divider()
    st.subheader("📤 Exportar historial de cambios")
    try:
        historial_df = pd.read_excel("base_datos_MAKE_Virosque.xlsx", sheet_name="Historial")
        csv = historial_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar historial en CSV", data=csv, file_name="historial_cambios.csv", mime="text/csv")
    except:
        st.info("No se ha encontrado ningún historial para exportar.")
