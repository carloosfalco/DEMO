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

def planificador_rutas():
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
            hora_carga = st.text_input(f"🕒 Hora de carga Origen {i+1}", key=f"hora_carga_{i}")
            ref_carga = st.text_input(f"🔖 Ref. de carga Origen {i+1}", key=f"ref_carga_{i}")
            origenes.append((origen.strip(), hora_carga.strip(), ref_carga.strip()))

        num_destinos = st.number_input("Número de ubicaciones de descarga", min_value=1, max_value=5, value=1)
        destinos = []
        for i in range(num_destinos):
            destino = st.text_input(f"🎯 Destino {i+1}", key=f"destino_{i}")
            fecha_descarga = st.date_input(f"📅 Fecha de descarga Destino {i+1}", value=date.today(), key=f"fecha_descarga_{i}")
            hora_descarga = st.text_input(f"🕓 Hora de descarga Destino {i+1}", key=f"hora_descarga_{i}")
            ref_cliente = st.text_input(f"📌 Referencia cliente Destino {i+1}", key=f"ref_cliente_{i}")
            destinos.append((destino.strip(), fecha_descarga, hora_descarga.strip(), ref_cliente.strip()))

        tipo_mercancia = st.text_input("📦 Tipo de mercancía (opcional)").strip()
        observaciones = st.text_area("📝 Observaciones (opcional)").strip()

        submitted = st.form_submit_button("Generar orden")

    if submitted:
        mensaje = f"Hola {chofer}," if chofer else "Hola,"
        mensaje += f" esta es la orden de carga para el día {formatear_fecha_con_dia(fecha_carga)}:\n\n"

        if ref_interna:
            mensaje += f"🔐 Ref. interna: {ref_interna}\n\n"

        cargas = []
        for i, (origen, hora, ref_carga) in enumerate(origenes):
            if origen:
                linea = f"  - Origen {i+1}: {origen}"
                if hora:
                    linea += f" ({hora}H)"
                cargas.append(linea)
                if ref_carga:
                    cargas.append(f"    ↪️ Ref. carga: {ref_carga}")
        if cargas:
            mensaje += "📍 Cargas:\n" + "\n".join(cargas) + "\n"

        descargas = []
        for i, (destino, fecha_descarga, hora_descarga, ref_cliente) in enumerate(destinos):
            if destino:
                linea = f"  - Destino {i+1}: {destino}"
                detalles = []
                if fecha_descarga:
                    detalles.append(formatear_fecha_con_dia(fecha_descarga))
                if hora_descarga:
                    detalles.append(hora_descarga)
                if detalles:
                    linea += f" ({', '.join(detalles)})"
                descargas.append(linea)
                if ref_cliente:
                    descargas.append(f"    ↪️ Ref. cliente: {ref_cliente}")
        if descargas:
            mensaje += "\n🎯 Descargas:\n" + "\n".join(descargas) + "\n"

        if tipo_mercancia:
            mensaje += f"\n📦 Tipo de mercancía: {tipo_mercancia}"

        if observaciones:
            mensaje += f"\n\n📌 {observaciones}"

        mensaje += "\n\nPor favor, avisa de inmediato si surge algún problema o hay riesgo de retraso."
        mensaje = mensaje.strip()

        st.markdown("### ✉️ Orden generada:")
        st.code(mensaje, language="markdown")
