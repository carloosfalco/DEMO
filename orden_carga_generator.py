import streamlit as st
import pandas as pd

def generar_instrucciones_ruta():
    st.title("🚛 Instrucciones de Ruta para el Conductor")

    uploaded_file = st.file_uploader("📁 Sube el archivo Excel exportado de Trans2000", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, sheet_name=0)
            columnas = ['Fecha', 'Tipo', 'Nombre', 'Albarán', 'Domicilio', 'Población', 'Provincia', 'Palets']

            if not all(col in df.columns for col in columnas):
                st.error("❌ El archivo no contiene todas las columnas necesarias.")
                return

            df = df[columnas].sort_values(by=['Fecha', 'Tipo']).reset_index(drop=True)

            pedido = st.text_input("📝 Introduce el número de pedido:", placeholder="Ej: 4587")

            horas = []
            st.markdown("### ⏰ Introduce la hora de cada parada:")
            for i, row in df.iterrows():
                etiqueta = f"{row['Tipo'].capitalize()} - {row['Nombre']} ({row['Fecha'].strftime('%d/%m/%Y')})"
                hora = st.text_input(etiqueta, key=f"hora_{i}", placeholder="Ej: 08:30")
                horas.append(hora)

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

            st.markdown("### 📋 Mensaje final para WhatsApp:")
            st.code(instrucciones.strip(), language=None)
           

        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")
