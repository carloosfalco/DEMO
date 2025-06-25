def generar_orden_carga_manual():
    st.title("📦 Generador de Orden de Carga")
    st.markdown("Completa los siguientes datos para generar una orden.")

    if "num_origenes" not in st.session_state:
        st.session_state.num_origenes = 1
    if "num_destinos" not in st.session_state:
        st.session_state.num_destinos = 1

    # Botón "Ida y vuelta"
    if st.button("↔️ Ida y vuelta"):
        st.session_state.num_origenes = 2
        st.session_state.num_destinos = 2

    with st.form("orden_form"):
        chofer = st.text_input("Nombre del chofer", key="chofer")
        fecha_carga = st.date_input("Fecha de carga", value=st.session_state.get("fecha_carga", date.today()), key="fecha_carga")
        ref_interna = st.text_input("🔐 Referencia interna", key="ref_interna")

        incluir_todos_links = st.checkbox("🗸 Incluir enlaces de Google Maps para todas las ubicaciones", key="incluir_todos_links")

        num_origenes = st.number_input("Número de ubicaciones de carga", min_value=1, max_value=5,
                                       value=st.session_state.num_origenes, key="num_origenes")
        origenes = []
        for i in range(num_origenes):
            st.markdown(f"#### 📍 Origen {i+1}")
            origen = st.text_input(f"Dirección Origen {i+1}", key=f"origen_{i}")
            hora_carga = st.text_input(f"🕒 Hora de carga Origen {i+1}", key=f"hora_carga_{i}")
            ref_carga = st.text_area(f"🔖 Ref. de carga Origen {i+1}", key=f"ref_carga_{i}")
            _incluir_link = st.checkbox("Incluir enlace Maps", value=incluir_todos_links, key=f"link_origen_{i}")
            incluir_link = incluir_todos_links or _incluir_link
            origenes.append((origen.strip(), hora_carga.strip(), ref_carga.strip(), incluir_link))

        num_destinos = st.number_input("Número de ubicaciones de descarga", min_value=1, max_value=5,
                                       value=st.session_state.num_destinos, key="num_destinos")
        destinos = []
        for i in range(num_destinos):
            st.markdown(f"#### 📍 Destino {i+1}")
            destino = st.text_input(f"Dirección Destino {i+1}", key=f"destino_{i}")
            fecha_descarga_default = fecha_carga + timedelta(days=1)
            fecha_descarga = st.date_input(
                f"Fecha de descarga Destino {i+1}",
                value=st.session_state.get(f"fecha_descarga_{i}", fecha_descarga_default),
                key=f"fecha_descarga_{i}"
            )
            hora_descarga = st.text_input(f"🕓 Hora de descarga Destino {i+1}", key=f"hora_descarga_{i}")
            ref_cliente = st.text_area(f"📌 Referencia cliente Destino {i+1}", key=f"ref_cliente_{i}")
            _incluir_link = st.checkbox("Incluir enlace Maps", value=incluir_todos_links, key=f"link_destino_{i}")
            incluir_link = incluir_todos_links or _incluir_link
            destinos.append((destino.strip(), fecha_descarga, hora_descarga.strip(), ref_cliente.strip(), incluir_link))

        tipo_mercancia = st.text_input("📦 Tipo de mercancía (opcional)", key="tipo_mercancia").strip()
        observaciones = st.text_area("📜 Observaciones (opcional)", key="observaciones").strip()

        submitted = st.form_submit_button("Generar orden")

    # (el resto del código permanece igual para generar el mensaje...)
