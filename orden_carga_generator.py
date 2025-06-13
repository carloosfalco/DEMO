import streamlit as st
import pandas as pd

st.set_page_config(page_title="Orden de carga por WhatsApp", page_icon="📲", layout="wide")

st.title("📲 Generador de Mensajes de Carga para WhatsApp")
st.markdown("Sube el archivo de Trans2000 y copia los mensajes para enviar a los conductores.")

# Subida del archivo
uploaded_file = st.file_uploader("📁 Sube el archivo Excel de Trans2000", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Hoja1")

        # Filtrar solo cargas
        cargas = df[df['Tipo'].str.lower() == 'carga'].copy()

        # Generar mensajes
        mensajes = []
        for _, row in cargas.iterrows():
            msg = f"""🚛 *Orden de carga #{int(row['Orden']):03d}*

📅 Fecha: {row['Fecha'].strftime('%d/%m/%Y')}
🏢 Cliente: {row['Nombre']}
📦 Albarán: {row['Albarán']}
📍 Dirección: {row['Domicilio']}, {row['Población']} ({row['Provincia']})
📦 Palets: {int(row['Palets'])}
"""
            mensajes.append(msg)

        # Mostrar todos los mensajes con opción de copiar
        for i, msg in enumerate(mensajes):
            st.text_area(f"Mensaje {i+1}", value=msg, height=180, key=f"msg_{i}")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
