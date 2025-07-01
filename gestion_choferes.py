import streamlit as st
import pandas as pd

def gestion_choferes():
    st.title("🧑‍✈️ Gestión de chóferes")
    st.markdown("Visualiza y filtra los chóferes registrados desde el archivo CSV local.")

    try:
        df = pd.read_csv("choferes.csv")

        # Filtros superiores
        col1, col2, col3 = st.columns(3)
        jefe_filtrado = col1.selectbox("👨‍💼 Jefe de tráfico", ["Todos"] + sorted(df["Jefe de tráfico"].dropna().unique().tolist()))
        tipo_filtrado = col2.selectbox("🚛 Tipo", ["Todos"] + sorted(df["Tipo"].dropna().unique().tolist()))
        marca_filtrada = col3.selectbox("🚚 Marca Tractora", ["Todos"] + sorted(df["Marca Tractora"].dropna().unique().tolist()))

        # Aplicar filtros
        df_filtrado = df.copy()
        if jefe_filtrado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Jefe de tráfico"] == jefe_filtrado]
        if tipo_filtrado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_filtrado]
        if marca_filtrada != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Marca Tractora"] == marca_filtrada]

        st.markdown(f"**{len(df_filtrado)} chóferes encontrados.**")

        st.dataframe(df_filtrado, use_container_width=True)

    except FileNotFoundError:
        st.error("❌ No se encuentra el archivo 'choferes_limpio.csv'. Por favor, súbelo o verifica su ruta.")
    except Exception as e:
        st.error(f"❌ Error inesperado: {e}")
