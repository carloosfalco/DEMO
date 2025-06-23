import streamlit as st
import openrouteservice
import requests
import math
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from PIL import Image

def planificador_rutas():
    api_key = "5b3ce3597851110001cf6248ec3aedee3fa14ae4b1fd1b2440f2e589"
    client = openrouteservice.Client(key=api_key)

    st.markdown("""
        <style>
            body {
                background-color: #f5f5f5;
            }
            .stButton>button {
                background-color: #8D1B2D;
                color: white;
                border-radius: 6px;
                padding: 0.6em 1em;
                border: none;
                font-weight: bold;
            }
            .stButton>button:hover {
                background-color: #a7283d;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    logo = Image.open("logo-virosque2-01.png")
    st.image(logo, width=250)
    st.markdown("<h1 style='color:#8D1B2D;'>TMS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:white; font-size: 18px; font-weight: bold;'>Planificador de rutas para camiones</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        origen = st.text_input("\ud83d\udccd Origen", value="Valencia, Espa\u00f1a")
    with col2:
        destino = st.text_input("\ud83c\udf1f Destino", value="Madrid, Espa\u00f1a")
    with col3:
        hora_salida_str = st.time_input("\ud83d\udd52 Hora de salida", value=datetime.strptime("08:00", "%H:%M")).strftime("%H:%M")

    stops = st.text_area("\u2795 Paradas intermedias (una por l\u00ednea)", placeholder="Ej: Albacete, Espa\u00f1a\nCuenca, Espa\u00f1a")

    if st.button("\ud83d\udd0d Calcular Ruta"):
        st.session_state.resultados = None

        coord_origen, _ = geocode(origen, api_key)
        coord_destino, _ = geocode(destino, api_key)

        stops_list = []
        if stops.strip():
            for parada in stops.strip().split("\n"):
                coord, _ = geocode(parada, api_key)
                if coord:
                    stops_list.append(coord)
                else:
                    st.warning(f"\u274c No se pudo geolocalizar: {parada}")

        if not coord_origen or not coord_destino:
            st.error("\u274c No se pudo geolocalizar el origen o destino.")
            return

        coords_totales = [coord_origen] + stops_list + [coord_destino]

        preferencias = ["recommended", "fastest", "shortest"]
        rutas = []
        errores = []

        for pref in preferencias:
            try:
                ruta = client.directions(
                    coordinates=coords_totales,
                    profile='driving-hgv',
                    preference=pref,
                    format='geojson'
                )
                rutas.append((pref, ruta))
            except openrouteservice.exceptions.ApiError as e:
                errores.append((pref, str(e)))

        if not rutas:
            st.error("\u274c No se pudieron calcular rutas. Errores: " + ", ".join([f"{p}: {e}" for p, e in errores]))
            return

        ruta_principal = [r for r in rutas if r[0] == "recommended"][0][1]
        segmentos = ruta_principal['features'][0]['properties']['segments']
        distancia_total = sum(seg["distance"] for seg in segmentos)
        duracion_total = sum(seg["duration"] for seg in segmentos)

        distancia_km = distancia_total / 1000
        duracion_horas = duracion_total / 3600
        descansos = math.floor(duracion_horas / 4.5)
        tiempo_total_h = duracion_horas + descansos * 0.75
        descanso_diario_h = 11 if tiempo_total_h > 13 else 0
        tiempo_total_real_h = tiempo_total_h + descanso_diario_h
        hora_salida = datetime.strptime(hora_salida_str, "%H:%M")
        hora_llegada = hora_salida + timedelta(hours=tiempo_total_real_h)

        def horas_y_minutos(valor_horas):
            horas = int(valor_horas)
            minutos = int(round((valor_horas - horas) * 60))
            return f"{horas}h {minutos:02d}min"

        tiempo_conduccion_txt = horas_y_minutos(duracion_horas)
        tiempo_total_txt = horas_y_minutos(tiempo_total_h)

        st.session_state.resultados = {
            "distancia_km": distancia_km,
            "tiempo_conduccion_txt": tiempo_conduccion_txt,
            "tiempo_total_txt": tiempo_total_txt,
            "hora_llegada": hora_llegada.strftime("%H:%M"),
            "hora_llegada_dt": hora_llegada,
            "hora_salida_dt": hora_salida,
            "tiempo_total_real_h": tiempo_total_real_h,
            "rutas": rutas,
            "coord_origen": coord_origen,
            "stops_list": stops_list,
            "coord_destino": coord_destino
        }

    if "resultados" in st.session_state and st.session_state.resultados:
        r = st.session_state.resultados

        st.markdown("### \ud83d\udcca Datos de la ruta")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("\ud83d\udea3 Distancia", f"{r['distancia_km']:.2f} km")
        col2.metric("\ud83d\udd53 Conducci\u00f3n", r['tiempo_conduccion_txt'])
        col3.metric("\u23f1 Total (con descansos)", r['tiempo_total_txt'])
        col4.metric("\ud83d\udcc5 Llegada estimada", r['hora_llegada'])

        if r['tiempo_total_real_h'] > 13:
            st.warning("\u26a0\ufe0f El viaje excede la jornada m\u00e1xima (13h). Se ha a\u00f1adido un descanso obligatorio de 11h.")
        else:
            st.success("\ud83d\udfe2 El viaje puede completarse en una sola jornada de trabajo.")
            llegada_tras_descanso = r["hora_llegada_dt"] + timedelta(hours=11)
            cambia_dia = llegada_tras_descanso.date() > r["hora_llegada_dt"].date()
            etiqueta = " (d\u00eda siguiente)" if cambia_dia else ""
            col5.metric("\ud83d\udecc Llegada + descanso", llegada_tras_descanso.strftime("%H:%M") + etiqueta)

        linea_latlon = [[p[1], p[0]] for p in r["rutas"][0][1]["features"][0]["geometry"]["coordinates"]]
        m = folium.Map(location=linea_latlon[0], zoom_start=6)

        folium.Marker(location=[r['coord_origen'][1], r['coord_origen'][0]], tooltip="\ud83d\udccd Origen").add_to(m)
        for idx, parada in enumerate(r['stops_list']):
            folium.Marker(location=[parada[1], parada[0]], tooltip=f"Parada {idx + 1}").add_to(m)
        folium.Marker(location=[r['coord_destino'][1], r['coord_destino'][0]], tooltip="Destino").add_to(m)

        colores = ["blue", "green", "purple", "orange"]
        for i, (pref, ruta) in enumerate(r["rutas"]):
            coords = ruta["features"][0]["geometry"]["coordinates"]
            linea = [[p[1], p[0]] for p in coords]
            folium.PolyLine(linea, color=colores[i % len(colores)], weight=5, tooltip=f"Ruta: {pref}").add_to(m)

        st.markdown("### \ud83d\udd98\ufe0f Rutas alternativas en el mapa:")
        st_folium(m, width=1200, height=500)

def geocode(direccion, api_key):
    url = "https://api.openrouteservice.org/geocode/search"
    params = {
        "api_key": api_key,
        "text": direccion,
        "boundary.country": "ES",
        "size": 1
    }
    r = requests.get(url, params=params)
    data = r.json()
    if data.get("features"):
        coord = data["features"][0]["geometry"]["coordinates"]
        label = data["features"][0]["properties"]["label"]
        return coord, label
    else:
        return None, None
