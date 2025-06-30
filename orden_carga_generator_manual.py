from datetime import date, timedelta
import urllib.parse
import streamlit as st

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

    ida_vuelta = st.toggle("↔️ Ida y vuelta", value=st.session_state.get("ida_vuelta", False))
    st.session_state.ida_vuelta = ida_vuelta

    if ida_vuelta:
        num_origenes = 2
        num_destinos = 2
    else:
        num_origenes = st.number_input("Número de ubicaciones de carga", min_value=1, max_value=5,
                                       value=st.session_state.get("num_origenes", 1), key="num_origenes_input")
        num_destinos = st.number_input("Número de ubicaciones de descarga", min_value=1, max_value=5,
                                       value=st.session_state.get("num_destinos", 1), key="num_destinos_input")

    with st.form("orden_form"):
        chofer = st.text_input("Nombre del chofer", key="chofer")
        ref_interna = st.text_input("🔐 Referencia interna", key="ref_interna")
        incluir_todos_links = st.checkbox("Incluir enlaces de Google Maps para todas las ubicaciones", key="incluir_todos_links")

        origenes, destinos = [], []
        destino_1_val = ""

        if ida_vuelta:
            fechas_carga = []
            for i in range(2):
                st.markdown(f"#### 📍 Origen {i+1}")
                fecha_carga_i = st.date_input(f"Fecha de carga Origen {i+1}", key=f"fecha_carga_{i}", value=date.today())
                default_origen = destino_1_val if i == 1 else ""
                fechas_carga.append(fecha_carga_i)

                origen = st.text_input(f"Dirección Origen {i+1}", value=default_origen, key=f"origen_{i}")
                hora_carga = st.text_input(f"🕒 Hora de carga Origen {i+1}", key=f"hora_carga_{i}")
                ref_carga = st.text_area(f"🔖 Ref. de carga Origen {i+1}", key=f"ref_carga_{i}")
                _incluir_link = st.checkbox("Incluir enlace Maps", value=incluir_todos_links, key=f"link_origen_{i}")
                incluir_link = incluir_todos_links or _incluir_link
                origenes.append((origen.strip(), hora_carga.strip(), ref_carga.strip(), incluir_link))

                st.markdown(f"#### 📍 Destino {i+1}")
                destino = st.text_input(f"Dirección Destino {i+1}", key=f"destino_{i}")
                if i == 0:
                    destino_1_val = destino
                fecha_descarga = st.date_input(f"Fecha de descarga Destino {i+1}", value=date.today(), key=f"fecha_descarga_{i}")
                hora_descarga = st.text_input(f"🕓 Hora de descarga Destino {i+1}", key=f"hora_descarga_{i}")
                ref_cliente = st.text_area(f"📌 Referencia cliente Destino {i+1}", key=f"ref_cliente_{i}")
                _incluir_link = st.checkbox("Incluir enlace Maps", value=incluir_todos_links, key=f"link_destino_{i}")
                incluir_link = incluir_todos_links or _incluir_link
                destinos.append((destino.strip(), fecha_descarga, hora_descarga.strip(), ref_cliente.strip(), incluir_link))
        else:
            fecha_carga_unica = st.date_input("📅 Fecha de carga", value=date.today(), key="fecha_carga_unica")

            cols = st.columns([3, 2])
            with cols[0]:
                fecha_descarga_comun = st.date_input("📅 Fecha de descarga", key="fecha_descarga_comun", value=date.today() + timedelta(days=1))
            with cols[1]:
                entregar_de_seguido = st.checkbox("Entregar de seguido", key="entregar_de_seguido")
                if entregar_de_seguido:
                    fecha_descarga_comun = fecha_carga_unica

            for i in range(num_origenes):
                st.markdown(f"#### 📍 Origen {i+1}")
                origen = st.text_input(f"Dirección Origen {i+1}", key=f"origen_{i}")
                hora_carga = st.text_input(f"🕒 Hora de carga Origen {i+1}", key=f"hora_carga_{i}")
                ref_carga = st.text_area(f"🔖 Ref. de carga Origen {i+1}", key=f"ref_carga_{i}")
                _incluir_link = st.checkbox("Incluir enlace Maps", value=incluir_todos_links, key=f"link_origen_{i}")
                incluir_link = incluir_todos_links or _incluir_link
                origenes.append((origen.strip(), hora_carga.strip(), ref_carga.strip(), incluir_link))

            for i in range(num_destinos):
                st.markdown(f"#### 📍 Destino {i+1}")
                destino = st.text_input(f"Dirección Destino {i+1}", key=f"destino_{i}")
                hora_descarga = st.text_input(f"🕓 Hora de descarga Destino {i+1}", key=f"hora_descarga_{i}")
                ref_cliente = st.text_area(f"📌 Referencia cliente Destino {i+1}", key=f"ref_cliente_{i}")
                _incluir_link = st.checkbox("Incluir enlace Maps", value=incluir_todos_links, key=f"link_destino_{i}")
                incluir_link = incluir_todos_links or _incluir_link
                destinos.append((destino.strip(), fecha_descarga_comun, hora_descarga.strip(), ref_cliente.strip(), incluir_link))

        tipo_mercancia = st.text_input("📦 Tipo de mercancía (opcional)", key="tipo_mercancia").strip()
        observaciones = st.text_area("📜 Observaciones (opcional)", key="observaciones").strip()
        submitted = st.form_submit_button("Generar orden")

    if submitted:
        st.success("Orden generada correctamente ✅")
