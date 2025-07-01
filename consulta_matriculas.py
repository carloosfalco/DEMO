import streamlit as st
import pandas as pd
from datetime import datetime
import json
from google.oauth2 import service_account
import gspread

# Conexión segura usando st.secrets

def get_gsheet_connection():
    creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key("1KL9-HYhaSaSSRFirjxPNox24dVHOBlA2Zmny4G1GTj4")
    return sh

def normalizar_matricula(input_txt, df):
    input_txt = input_txt.upper().strip()
    if input_txt in df["Matrícula"].values:
        return input_txt
    posibles = df[df["Matrícula"].str.startswith(input_txt)]
    if not posibles.empty:
        return posibles.iloc[0]["Matrícula"]
    return input_txt

def consulta_matriculas():
    st.title("🔍 Consulta de matrículas")

    sh = get_gsheet_connection()
    choferes_df = pd.DataFrame(sh.worksheet("Chóferes").get_all_records())
    remolques_df = pd.DataFrame(sh.worksheet("Remolques").get_all_records())
    tractoras_df = pd.DataFrame(sh.worksheet("Tractoras").get_all_records())

    matricula_input = st.text_input("Introduce una matrícula de tractora o remolque:").upper().strip()

    if matricula_input:
        tractora_input = normalizar_matricula(matricula_input, tractoras_df)
        remolque_input = normalizar_matricula(matricula_input, remolques_df)

        tractora_row = tractoras_df[tractoras_df["Matrícula"] == tractora_input]
        if not tractora_row.empty:
            chofer = tractora_row.iloc[0]["Chofer asignado"]
            remolque = tractora_row.iloc[0]["Remolque asignado"]
            jefe = choferes_df[choferes_df["Chofer"] == chofer]["Jefe de tráfico"].values[0] if chofer in choferes_df["Chofer"].values else "Desconocido"
            tipo_remolque = remolques_df[remolques_df["Matrícula"] == remolque]["Tipo"].values[0] if remolque in remolques_df["Matrícula"].values else "Desconocido"
            st.success(f"La tractora {tractora_input} la conduce {chofer} junto al remolque {remolque} ({tipo_remolque}) y su jefe de tráfico es {jefe}.")
        else:
            remolque_row = remolques_df[remolques_df["Matrícula"] == remolque_input]
            if not remolque_row.empty:
                chofer = remolque_row.iloc[0]["Chofer asignado"]
                tractora = remolque_row.iloc[0]["Tractora asignada"]
                tipo = remolque_row["Tipo"].values[0]
                jefe = choferes_df[choferes_df["Chofer"] == chofer]["Jefe de tráfico"].values[0] if chofer in choferes_df["Chofer"].values else "Desconocido"
                st.success(f"El remolque {remolque_input} (tipo {tipo}) está asignado a {chofer}, que conduce la tractora {tractora} bajo la supervisión de {jefe}.")
            else:
                st.error("Matrícula no encontrada en el sistema.")

    st.divider()
    st.title("🔁 Registro de cambios de asignación")

    st.subheader("Formulario de cambio")
    chofer = st.selectbox("Chofer que realiza el cambio:", choferes_df["Chofer"].unique())

    remolque_asignado = choferes_df[choferes_df["Chofer"] == chofer]["Remolque asignado"].values[0]
    tractora_asignada = choferes_df[choferes_df["Chofer"] == chofer]["Tractora asignada"].values[0]

    cambiar_remolque = st.checkbox("Modificar remolque")
    if cambiar_remolque:
        remolque_actual = st.text_input("Remolque que deja (si aplica):", value=remolque_asignado).upper().strip()
        estado_remolque = st.selectbox("Estado del remolque que deja:", ["", "Disponible", "Mantenimiento", "Baja"])
        remolque_nuevo = st.text_input("Nuevo remolque que asume (si aplica):").upper().strip()
    else:
        remolque_actual = remolque_nuevo = estado_remolque = None

    cambiar_tractora = st.checkbox("Modificar tractora")
    if cambiar_tractora:
        tractora_actual = st.text_input("Tractora que deja (si aplica):", value=tractora_asignada).upper().strip()
        estado_tractora = st.selectbox("Estado de la tractora que deja:", ["", "Disponible", "Mantenimiento", "Baja"])
        tractora_nueva = st.text_input("Nueva tractora que asume (si aplica):").upper().strip()
    else:
        tractora_actual = tractora_nueva = estado_tractora = None

    confirmar = st.button("Registrar cambio")

    if confirmar:
        evento = f"{chofer} deja tractora {tractora_actual or 'ninguna'} ({estado_tractora or 'sin cambio'}) y asume {tractora_nueva or 'ninguna'}, deja remolque {remolque_actual or 'ninguno'} ({estado_remolque or 'sin cambio'}) y asume {remolque_nuevo or 'ninguno'}"
        nueva_fila = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), evento]
        historial_ws = sh.worksheet("Historial")
        historial_ws.append_row(nueva_fila)
        st.success("✅ Cambio registrado correctamente en Google Sheets.")

    st.divider()
    st.subheader("📤 Exportar historial")
    historial_df = pd.DataFrame(sh.worksheet("Historial").get_all_records())
    st.dataframe(historial_df)
    csv = historial_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar historial en CSV", data=csv, file_name="historial_cambios.csv", mime="text/csv")
