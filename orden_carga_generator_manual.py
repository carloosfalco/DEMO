import streamlit as st
from datetime import date, timedelta
import urllib.parse

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
    st.title("Generador de Orden de Carga")
    st.markdown("Completa los siguientes datos para generar una orden.")

    ida_vuelta = st.toggle("⇄ Ida y vuelta", value=st.session_state.get("ida_vuelta", False))
    st.session_state.ida_vuelta = ida_vuelta

    # Check adicional: Necesario cinchado
    necesario_cinchado = st.checkbox("Necesario cinchado", key="necesario_cinchado")

    if not ida_vuelta:
        entregar_de_seguido = st.checkbox("Entregar de seguido", key="entregar_seguido")

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
        incluir_todos_links = st.checkbox("Incluir enlaces de Google Maps para todas las ubicaciones", key="incluir_todos_links")

        origenes, destinos = [], []
        destino_1_val = ""

        if ida_vuelta:
            fechas_carga = []
            for i in range(2):
                st.markdown(f"#### 📍 Origen {i+1}")
                fecha_carga_i = st.date_input(f"Fecha de carga Origen {i+1}", key=f"fecha_carga_{i}", value=date.today())
                fechas_carga.append(fecha_carga_i)
                default_origen = destino_1_val if i == 1 else ""
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
                ref_cliente = st.text_area(f"🔖 Referencia cliente Destino {i+1}", key=f"ref_cliente_{i}")
                _incluir_link = st.checkbox("Incluir enlace Maps", value=incluir_todos_links, key=f"link_destino_{i}")
                incluir_link = incluir_todos_links or _incluir_link
                destinos.append((destino.strip(), fecha_descarga, hora_descarga.strip(), ref_cliente.strip(), incluir_link))
        else:
            fecha_carga_unica = st.date_input("Fecha de carga", value=date.today(), key="fecha_carga_unica")
            if st.session_state.entregar_seguido:
                fecha_descarga_comun = fecha_carga_unica
            else:
                fecha_descarga_comun = st.date_input("Fecha de descarga", value=fecha_carga_unica + timedelta(days=1), key="fecha_descarga_comun")

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

        temperatura_refrigerado = st.text_input("🌡️ Temperatura", key="temp_refrigerado").strip()
        observaciones = st.text_area("📜 Observaciones (opcional)", key="observaciones").strip()
        ref_interna = st.text_input("🔐 Referencia interna", key="ref_interna")

        submitted = st.form_submit_button("Generar orden")

    if submitted:
        mensaje = f"Hola {chofer}," if chofer else "Hola,"
        mensaje += f" esta es la orden de carga:\n\n"

        bloques = []
        if ida_vuelta:
            for i in range(2):
                bloque = []
                if origenes[i][0]:
                    bloque.append(f"📍 Carga {i+1} ({formatear_fecha_con_dia(fechas_carga[i])}):")
                    linea = f"  - *{origenes[i][0]}*"
                    if origenes[i][1]:
                        linea += f" ({origenes[i][1]})"
                    bloque.append(linea)
                    if origenes[i][2]:
                        ref_lines = origenes[i][2].splitlines()
                        bloque.append(f"    Ref. carga:")
                        for line in ref_lines:
                            bloque.append(f"      {line}")
                    if origenes[i][3]:
                        bloque.append(f"    🌐 {generar_enlace_maps(origenes[i][0])}")

                if destinos[i][0]:
                    bloque.append(f"📍 Descarga {i+1} ({formatear_fecha_con_dia(destinos[i][1])}):")
                    linea = f"  - *{destinos[i][0]}*"
                    if destinos[i][2]:
                        linea += f" ({destinos[i][2]})"
                    bloque.append(linea)
                    if destinos[i][3]:
                        ref_lines = destinos[i][3].splitlines()
                        bloque.append(f"    Ref. cliente: {ref_lines[0]}")
                        for line in ref_lines[1:]:
                            bloque.append(f"                     {line}")
                    if destinos[i][4]:
                        bloque.append(f"    🌐 {generar_enlace_maps(destinos[i][0])}")
                bloques.append("\n".join(bloque))
        else:
            cargas = []
            for i, (origen, hora, ref_carga, incluir_link) in enumerate(origenes):
                if origen:
                    linea = f"  - *{origen}*"
                    if hora:
                        linea += f" ({hora})"
                    cargas.append(linea)
                    if ref_carga:
                        ref_lines = ref_carga.splitlines()
                        cargas.append(f"    Ref. carga:")
                        for line in ref_lines:
                            cargas.append(f"      {line}")
                    if incluir_link:
                        cargas.append(f"    🌐 {generar_enlace_maps(origen)}")
            if cargas:
                mensaje += f"📍 Cargas ({formatear_fecha_con_dia(fecha_carga_unica)}):\n" + "\n".join(cargas) + "\n"

            descargas = []
            for i, (destino, _, hora_descarga, ref_cliente, incluir_link) in enumerate(destinos):
                if destino:
                    linea = f"  - *{destino}*"
                    if hora_descarga:
                        linea += f" ({hora_descarga})"
                    descargas.append(linea)
                    if ref_cliente:
                        ref_lines = ref_cliente.splitlines()
                        descargas.append(f"    Ref. cliente: {ref_lines[0]}")
                        for line in ref_lines[1:]:
                            descargas.append(f"                     {line}")
                    if incluir_link:
                        descargas.append(f"    🌐 {generar_enlace_maps(destino)}")
            if descargas:
                mensaje += f"\n📍 Descargas ({formatear_fecha_con_dia(fecha_descarga_comun)}):\n" + "\n".join(descargas) + "\n"

        mensaje += "\n\n".join(bloques)

        if temperatura_refrigerado:
            mensaje += f"\n\n🌡️ Temperatura: {temperatura_refrigerado} en continuo, envía foto del display en el sitio de carga."

        if necesario_cinchado:
            mensaje += f"\n\n📦 En esta carga será necesaria la estiva."

        if observaciones:
            mensaje += f"\n\n📌 {observaciones}"

        if ref_interna:
            mensaje += f"\n\n🔐 Ref. interna: {ref_interna}"

        if ida_vuelta:
            mensaje += "\n\n🔁 Este es un viaje de ida y vuelta"

        if not ida_vuelta and st.session_state.entregar_seguido:
            mensaje += "\n\n🚛 Entrega de seguido (fecha de descarga igual a la de carga)."

        mensaje += "\n\nPor favor, avisa de inmediato si surge algún problema o hay riesgo de retraso."

        st.markdown("### ✉️ Orden generada:")
        st.code(mensaje.strip(), language="markdown")
