import streamlit as st
import pandas as pd

st.set_page_config(page_title="Resumen de Cargas y Descargas", page_icon="📲", layout="wide")
st.title("📲 Instrucciones de Ruta para el Conductor")

uploaded_file = st.file_uploader("📁 Sube el archivo Excel de Trans2000", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        st.subheader("Vista previa del archivo cargado:")
        st.dataframe(df.head())  # <-- Aquí ves si todo está bien

        # Revisa las columnas presentes
        columnas_necesarias = ['Fecha', 'Tipo', 'Nombre', 'Albarán', 'Domicilio', 'Población', 'Provincia', 'Palets']
        columnas_presentes = [col for col in columnas_necesarias if col in df.columns]

        if len(columnas_presentes) < len(columnas_necesarias):
            st.warning(f"Faltan columnas: {set(columnas_necesarias) - set(columnas_presentes)}")
        else:
            df = df[columnas_necesarias].sort_values(by=['Fecha', 'Tipo']).reset_index(drop=True)

            # ✅ Entrada manual de pedido
            pedido = st.text_input("📝 Introduce el número de pedido:", placeholder="Ej: 4587")

            # ✅ Entradas de hora por parada
            horas = []
            st.markdown("### ⏰ Introduce la hora de cada parada:")
            for i, row in df.iterrows():
                etiqueta = f"{row['Tipo'].capitalize()} - {row['Nombre']} ({row['Fecha'].strftime('%d/%m/%Y')})"
                hora = st.text_input(etiqueta, key=f"hora_{i}", placeholder="Ej: 08:30")
                horas.append(hora)

            # ✅ Generación del mensaje
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
            st.download_button("📥 Descargar como .txt", instrucciones.strip(), file_name="instrucciones_ruta.txt")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
