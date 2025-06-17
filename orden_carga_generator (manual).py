import streamlit as st
from datetime import date

def generar_orden_carga():
    st.title("📦 Generador de Orden de Carga")
    st.markdown("Completa los siguientes datos para generar una orden.")

    with st.form("orden_form"):
        chofer = st.text_input("Nombre del chofer")
        fecha_carga = st.date_input("📅 Fecha de carga", value=date.today())
        ref_interna = st.text_input("🔐 Referencia interna")

        num_origenes = st.number_input("Número de ubicaciones de carga", min_value=1, max_value=5, value=1)
        origenes = []
        for i in range(num_origenes):
            origen = st.text_input(f"📍 Origen {i+1}", key=f"origen_{i}")
            hora_carga = st.time_input(f"🕒 Hora de carga Origen {i+1}", key=f"hora_carga_{i}")
            origenes.append((origen, hora_carga))

        num_destinos = st.number_input("Número de ubicaciones de descarga", min_value=1, max_value=5, value=1)
        destinos = []
        for i in range(num_destinos):
            destino = st.text_input(f"🎯 Destino {i+1}", key=f"destino_{i}")
            hora_descarga = st.text_input(f"🕓 Hora de descarga Destino {i+1}", key=f"hora_descarga_{i}")
            ref_cliente = st.text_input(f"📌 Referencia cliente Destino {i+1}", key=f"ref_cliente_{i}")
            destinos.append((destino, hora_descarga, ref_cliente))

        tipo_mercancia = st.text_input("📦 Tipo de mercancía (opcional)")
        observaciones = st.text_area("📝 Observaciones (opcional)")

        submitted = st.form_submit_button("Generar orden")

    if submitted:
        mensaje = f"Hola {chofer}, esta es la orden de carga para el día {fecha_carga.strftime('%d/%m/%Y')}:\n\n"
        mensaje += f"🔐 Ref. interna: {ref_interna}\n\n📍 Cargas:\n"

        for i, (origen, hora) in enumerate(origenes):
            if origen.strip():
                mensaje += f"  - Origen {i+1}: {origen} ({hora.strftime('%H:%M')}H)\n"

        mensaje += "\n🎯 Descargas:\n"
        for i, (destino, hora_descarga, ref) in enumerate(destinos):
            if destino.strip():
                mensaje += f"  - Destino {i+1}: {destino} ({hora_descarga}, Ref. cliente: {ref})\n"

        if tipo_mercancia.strip():
            mensaje += f"\n📦 Tipo de mercancía: {tipo_mercancia.strip()}"

        if observaciones.strip():
            mensaje += f"\n\n📌 {observaciones.strip()}"

        mensaje += "\n\nPor favor, avisa de inmediato si surge algún problema o hay riesgo de retraso."
        mensaje = mensaje.strip()

        st.markdown("### ✉️ Orden generada:")
        st.code(mensaje, language="markdown")

