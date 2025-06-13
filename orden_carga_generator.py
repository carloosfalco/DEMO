import streamlit as st
import pandas as pd

st.set_page_config(page_title="Resumen de Cargas y Descargas", page_icon="📲", layout="wide")

st.title("📲 Instrucciones de Ruta para el Conductor")
st.markdown("Sube el archivo de Trans2000 y rellena los datos manuales para generar el mensaje final.")

# Subida del archivo
uploaded_file = st.file_uploader("📁 Sube el archivo Excel de Trans2000", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Hoja1")

        # Filtrar columnas clave y ordenar
        df = df[['Fecha', 'Tipo', 'Nombre', 'Albarán', 'Domicilio', 'Población', 'Provincia', 'Palets']]
        df = df.sort_values(by=['Fecha', 'Tipo'], ascending=[True, True]).reset_index(drop=True)

        # Entrada del número de pedido
        pedido = st.text_input("📝 Introduce el número de pedido:", placeholder="Ej: 567890")

        # Entrada de horas por cada parada
        horas = []
        st.markdown("### ⏰ Introduce la hora de cada parada:")
        for i, row in df.iterrows():
            label = f"{row['Tipo'].capitalize()} - {row['Nombre']} ({row['Fecha'].strftime('%d/%m/%Y')})"
            hora = st.text_input(label, key=f"hora_{i}", placeholder="Ej: 08:30")
            horas.append(hora)

        # Generar mensaje final
        instrucciones = "🚛 *INSTRUCCIONES DE RUTA*\n\n"
        instrucciones += f"📝 Nº de pedido: {pedido if pedido else '________'}\n\n"

        for i, row in df.iterrows():
            tipo = "*CARGA*" if row['Tipo'].lower() == 'carga' else "*DESCARGA*"
            instrucciones += (
                f"🔹 {tipo} - {row['Fecha'].strftime('%d/%m/%Y')}\n"
                f"⏰ Hora: {horas[i] if horas[i] else '________'}\n"
                f"📍 {row['Nombre']}\n"
                f"🏠 {row['Domicilio']}, {row['Población']} ({row['Provincia']})\n"
                f"📦 Albarán: {row['Albarán']} | Palets: {int(row['Palets'])}\n\n"
            )

        mensaje_final = instrucciones.strip()

        # Mostrar mensaje con botón copiar
        st.markdown("### 📋 Mensaje final para WhatsApp:")
        st.code(mensaje_final, language=None)
        st.download_button("📥 Descargar mensaje como .txt", mensaje_final, file_name="instrucciones_ruta.txt")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
