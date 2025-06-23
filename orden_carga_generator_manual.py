import streamlit as st
from datetime import date

# Diccionario para traducir días de la semana
DIAS_SEMANA_ES = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

def formatear_fecha_con_dia(fecha):
    dia_en = fecha.strftime('%A')  # Día en inglés
    dia_es = DIAS_SEMANA_ES.get(dia_en, dia_en)  # Traducir al español
    return f"{dia_es} {fecha.strftime('%d/%m')}"

def generar_orden_carga_manual():
    st.title("📦 Generador de Orden de Carga")
    st.markdown("Completa los siguientes datos para generar una orden.")

    with st.form("orden_form"):
        chofer = st.text_input("Nombre del chofer")
        fecha_carga = st.date_input("📅 Fecha de carga", value=date.today())
        ref_interna = st.text_area("🔐 Referencia interna", height=60)

        num_origenes = st.number_input("Número de ubicaciones de carga", min_value=1, max_value=5, value=1)
        origenes = []
        for i in range(num_origenes):
            origen = st.text_input(f"📍 Origen {i+1}", key=f"origen_{i}")
            hora_carga = st.text_input(f"🕒 Hora de carga Origen {i+1}", key=f"hora_carga_{i}")
            ref_carga = st.text_area(f"🔖 Ref. de carga Origen {i+1}", key=f"ref_carga_{i}", height=60)
            origenes.append((origen, hora_carga, ref_carga))

        num_destinos = st.number_input("Número de ubicaciones de descarga", min_value=1, max_value=5, value=1)
        destinos = []
        for i in range(num_destinos):
            destino = st.text_input(f"🎯 Destino {i+1}", key=f"destino_{i}")
            fecha_descarga = st.date_input(f"📅 Fecha de descarga Destino {i+1}", value=date.today(), key=f"fecha_descarga_{i}")
            hora_descarga = st.text_input(f"🕓 Hora de descarga Destino {i+1}", key=f"hora_descarga_{i}")
            ref_cliente = st.text_area(f"📌 Referencia cliente Destino {i+1}", key=f"ref_cliente_{i}", height=60)
            destinos.append((destino, fecha_descarga, hora_descarga, ref_cliente))

        tipo_mercancia = st.text_input("📦 Tipo de mercancía (opcional)")
        observaciones = st.text_area("📝 Observaciones (opcional)", height=80)

        submitted = st.form_submit_button("Generar orden")

    if submitted:
        mensaje = f"Hola {chofer}, esta es la orden de carga para el día {formatear_fecha_con_dia(fecha_carga)}:\n\n"
        mensaje += f"🔐 Ref. interna: {ref_interna.strip()}\n\n📍 Cargas:\n"

        for i, (origen, hora, ref_carga) in enumerate(origenes):
            if origen.strip():
                linea = f"  - Origen {i+1}: {origen} ({hora}H)"
                if ref_carga.strip():
                    linea += f", Ref. carga: {ref_carga.strip()}"
                mensaje += linea + "\n"

        mensaje += "\n🎯 Descargas:\n"
        for i, (destino, fecha_descarga, hora_descarga, ref) in enumerate(destinos):
            if destino.strip():
                mensaje += f"  - Destino {i+1}: {destino} ({formatear_fecha_con_dia(fecha_descarga)}, {hora_descarga}, Ref. cliente: {ref.strip()})\n"

        if tipo_mercancia.strip():
            mensaje += f"\n📦 Tipo de mercancía: {tipo_mercancia.strip()}"

        if observaciones.strip():
            mensaje += f"\n\n📌 {observaciones.strip()}"

        mensaje += "\n\nPor favor, avisa de inmediato si surge algún problema o hay riesgo de retraso."
        mensaje = mensaje.strip()

        st.markdown("### ✉️ Orden generada:")
        st.code(mensaje, language="markdown")

