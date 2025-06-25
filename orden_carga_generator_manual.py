import streamlit as st
from datetime import date
import urllib.parse

# Diccionario para traducir días de la semana
DIAS_SEMANA_ES = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}

def formatear_fecha_con_dia(fecha):
    dia_en = fecha.strftime('%A')
    dia_es = DIAS_SEMANA_ES.get(dia_en, dia_en)
    return f"{dia_es} {fecha.strftime('%d/%m')}"

def generar_enlace_maps(ubicacion):
    query = urllib.parse.quote_plus(ubicacion)
    return f"https://www.google.com/maps/search/?api=1&query={query}"

def generar_orden_carga_manual():
    st.title("📦 Generador de Orden de Carga")
    st.markdown("Completa los siguientes datos para generar una orden.")

    reiniciar = st.session_state.get("reiniciar", False)

    if reiniciar:
        for key in list(st.session_state.keys()):
            if key.startswith((
                "chofer", "fecha_carga", "ref_interna", "tipo_mercancia", "observaciones",
                "origen_", "hora_carga_", "ref_carga_", "link_origen_",
                "destino_", "fecha_descarga_", "hora_descarga_", "ref_cliente_", "link_destino_",
                "num_origenes", "num_destinos", "incluir_todos_links"
            )):
                del st.session_state[key]
        st.session_state["reiniciar"] = False
        st.experimental_rerun()

    with st.form("orden_form"):
        chofer = st.text_input("Nombre del chofer", key="chofer")
        fecha_carga = st.date_input("📅 Fecha de carga", value=st.session_state.get("fecha_carga", date.today()), key="fecha_carga")
        ref_interna = st.text_input("🔐 Referencia interna", key="ref_interna")

        incluir_todos_links = st.checkbox("🗺 Incluir enlaces de Google Maps para todas las ubicaciones", key="incluir_todos_links")

        num_origenes = st.number_input("Número de ubicaciones de carga", min_value=1, max_value=5, value=st.session_state.get("num_origenes", 1), key="num_origenes")
        origenes = []
        for i in range(num_origenes):
            st.markdown(f"#### 📍 Origen {i+1}")
            origen = st.text_input(f"Dirección Origen {i+1}", key=f"origen_{i}")
            hora_carga = st.text_input(f"🕒 Hora de carga Origen {i+1}", key=f"hora_carga_{i}")
            ref_carga = st.text_area(f"🔖 Ref. de carga Origen {i+1}", key=f"ref_carga_{i}")
            _incluir_link = st.checkbox("Incluir enlace Maps", value=incluir_todos_links, key=f"link_origen_{i}")
            incluir_link = incluir_todos_links or _incluir_link
            origenes.append((origen.strip(), hora_carga.strip(), ref_carga.strip(), incluir_link))

        num_destinos = st.number_input("Número de ubicaciones de descarga", min_value=1, max_value=5, value=st.session_state.get("num_destinos", 1), key="num_destinos")
        destinos = []
        for i in range(num_destinos):
            st.markdown(f"#### 📍 Destino {i+1}")
            destino = st.text_input(f"Dirección Destino {i+1}", key=f"destino_{i}")
            fecha_descarga = st.date_input(f"📅 Fecha de descarga Destino {i+1}", value=st.session_state.get(f"fecha_descarga_{i}", date.today()), key=f"fecha_descarga_{i}")
            hora_descarga = st.text_input(f"🕓 Hora de descarga Destino {i+1}", key=f"hora_descarga_{i}")
            ref_cliente = st.text_area(f"📌 Referencia cliente Destino {i+1}", key=f"ref_cliente_{i}")
            _incluir_link = st.checkbox("Incluir enlace Maps", value=incluir_todos_links, key=f"link_destino_{i}")
            incluir_link = incluir_todos_links or _incluir_link
            destinos.append((destino.strip(), fecha_descarga, hora_descarga.strip(), ref_cliente.strip(), incluir_link))

        tipo_mercancia = st.text_input("📦 Tipo de mercancía (opcional)", key="tipo_mercancia").strip()
        observaciones = st.text_area("📝 Observaciones (opcional)", key="observaciones").strip()

        submitted = st.form_submit_button("Generar orden")

    if submitted:
        mensaje = f"Hola {chofer}," if chofer else "Hola,"
        mensaje += f" esta es la orden de carga para el día {formatear_fecha_con_dia(fecha_carga)}:\n\n"

        if ref_interna:
            mensaje += f"🔐 Ref. interna: {ref_interna}\n\n"

        cargas = []
        for i, (origen, hora, ref_carga, incluir_link) in enumerate(origenes):
            if origen:
                linea = f"  - Origen {i+1}: {origen}"
                if hora:
                    linea += f" ({hora}H)"
                cargas.append(linea)
                if ref_carga:
                    ref_lines = ref_carga.splitlines()
                    cargas.append(f"    ↪️ Ref. carga: {ref_lines[0]}")
                    for line in ref_lines[1:]:
                        cargas.append(f"                   {line}")
                if incluir_link:
                    enlace = generar_enlace_maps(origen)
                    cargas.append(f"    🌐 {enlace}")
        if cargas:
            mensaje += f"📍 Cargas ({formatear_fecha_con_dia(fecha_carga)}):\n" + "\n".join(cargas) + "\n"

        descargas = []
        for i, (destino, fecha_descarga, hora_descarga, ref_cliente, incluir_link) in enumerate(destinos):
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
                    ref_lines = ref_cliente.splitlines()
                    descargas.append(f"    ↪️ Ref. cliente: {ref_lines[0]}")
                    for line in ref_lines[1:]:
                        descargas.append(f"                     {line}")
                if incluir_link:
                    enlace = generar_enlace_maps(destino)
                    descargas.append(f"    🌐 {enlace}")
        if descargas:
            mensaje += "\n📍 Descargas:\n" + "\n".join(descargas) + "\n"

        if tipo_mercancia:
            mensaje += f"\n📦 Tipo de mercancía: {tipo_mercancia}"

        if observaciones:
            mensaje += f"\n\n📌 {observaciones}"

        mensaje += "\n\nPor favor, avisa de inmediato si surge algún problema o hay riesgo de retraso."
        st.markdown("### ✉️ Orden generada:")
        st.code(mensaje.strip(), language="markdown")

       
        if st.button("🧹 Nueva orden"):
            st.session_state["reiniciar"] = True
            st.experimental_rerun()
