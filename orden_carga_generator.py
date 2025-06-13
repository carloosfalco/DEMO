import streamlit as st
import pandas as pd

st.set_page_config(page_title="Resumen de Cargas y Descargas", page_icon="📲", layout="wide")

st.title("📲 Instrucciones de Ruta para el Conductor")
st.markdown("Sube el archivo de Trans2000. El mensaje incluirá espacios para rellenar manualmente horas y nº de pedido.")

# Subida del archivo
uploaded_file = st.file_uploader("📁 Sube el archivo Excel de Trans2000", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Hoja1")

        # Filtrar columnas clave y ordenar
        df = df[['Fecha', 'Tipo', 'Nombre', 'Albarán', 'Domicilio', 'Población', 'Provincia', 'Palets']]
        df = df.sort_values(by=['Fecha', 'Tipo'], ascending=[True, True])

        instrucciones = "🚛 *INSTRUCCIONES DE RUTA*\n\n"
        for _, row in df.iterrows():
            tipo = "*CARGA*" if row['Tipo'].lower() == 'carga' else "*DESCARGA*"
            instrucciones += (
                f"🔹 {tipo} - {row['Fecha'].strftime('%d/%m/%Y')}\n"
                f"⏰ Hora: ________\n"
                f"📝 Pedido: ________\n"
                f"📍 {row['Nombre']}\n"
                f"🏠 {row['Domicilio']}, {row['Población']} ({row['Provincia']})\n"
                f"📦 Albarán: {row['Albarán']} | Palets: {int(row['Palets'])}\n\n"
            )

        st.text_area("Mensaje único para enviar por WhatsApp", value=instrucciones.strip(), height=600)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
