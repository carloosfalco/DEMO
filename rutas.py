import streamlit as st
import requests
import math
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from PIL import Image
import polyline

# 💡 Sustituye con tu propia API Key de Google
GOOGLE_API_KEY = "AIzaSyCt_46YfpaWYdW3DTRivVj2YX-xBgfbEus"

def geocode_google(direccion, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": direccion, "key": api_key}
    r = requests.get(url, params=params).json()

    if r.get("status") == "OK" and r.get("results"):
        location = r["results"][0]["geometry"]["location"]
        return [location["lng"], location["lat"]], r["results"][0]["formatted_address"]
    else:
        st.error(f"❌ Error al geolocalizar: '{direccion}'")
        st.code(f"Status: {r.get('status')}")
        if "error_message" in r:
            st.warning(f"🔍 Mensaje de Google: {r['error_message']}")
        st.info("🔧 Verifica la dirección o tu API Key.")
        return None, None

def obtener_ruta_google(coordenadas, api_key):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    origen = f"{coordenadas[0][1]},{coordenadas[0][0]}"
    destino = f"{coordenadas[-1][1]},{coordenadas[-1][0]}"
    waypoints = "|".join([f"{p[1]},{p[0]}" for p in coordenadas[1:-1]]) if len(coordenadas) > 2 else ""

    params = {
        "origin": origen,
        "destination": destino,
        "waypoints": waypoints,
        "mode": "driving",
        "key": api_key
    }

    r = requests.get(url, params=params).json()

    if r.get("status") == "OK":
        ruta = r["routes"][0]
        distancia_total = sum(leg["distance"]["value"] for leg in ruta["legs"])
        duracion_total = sum(leg["duration"]["value"] for leg in ruta["legs"])
        polyline_str = ruta["overview_polyline"]["points"]
        return distancia_total, duracion_total, polyline_str
    else:
        st.error("❌ No se pudo calcular la ruta.")
        st.code(f"Status: {r.get('status')}")
        if "error_message" in r:
            st.warning(f"🔍 Mensaje de Google: {r['error_message']}")
        st.info("🔧 Verifica las coordenadas o límites de la API.")
        return None, None, None

def planificador_rutas():
    st.markdown("""
        <style>
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
        origen = st.text_input("📍 Origen", value="Valencia, España")
    with col2:
        destino = st.text_input("🏁 Destino", value="Madrid, España")
    with col3:
        hora_salida_str = st.time_input("🕒 Hora de salida", value=datetime.strptime("08:00", "%H:%M")).strftime("%H:%M")

    stops = st.text_area("➕ Paradas intermedias (una por línea)", placeholder="Ej: Albacete, España\nCuenca, España")

    if st.button("🔍 Calcular Ruta"):
        st.session_state.resultados = None

        coord_origen, _ = geocode_google(origen, GOOGLE_API_KEY)
        coord_destino, _ = geocode_google(destino, GOOGLE_API_KEY)

        stops_list = []
        if stops.strip():
            for parada in stops.strip().split("\n"):
                coord, _ = geocode_google(parada, GOOGLE_API_KEY)
                if coord:
                    stops_list.append(coord)
                else:
                    st.warning(f"❌ No se pudo geolocalizar: {parada}")

        if not coord_origen or not coord_destino:
            st.error("❌ No se pudo geolocalizar el origen o destino.")
            return

        coords_totales = [coord_origen] + stops_list + [coord_destino]
        distancia, duracion, poly = obtener_ruta_google(coords_totales, GOOGLE_API_KEY)

        if not poly:
            return

        distancia_km = distancia / 1000
        duracion_horas = duracion / 3600
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
            "linea": polyline.decode(poly),
            "coord_origen": coord_origen,
            "stops_list": stops_list,
            "coord_destino": coord_destino
        }

    if "resultados" in st.session_state and st.session_state.resultados:
        r = st.session_state.resultados

        st.markdown("### 📊 Datos de la ruta")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🚣 Distancia", f"{r['distancia_km']:.2f} km")
        col2.metric("🕓 Conducción", r['tiempo_conduccion_txt'])
        col3.metric("⏱ Total (con descansos)", r['tiempo_total_txt'])
        col4.metric("📅 Llegada estimada", r['hora_llegada'])

        if r['tiempo_total_real_h'] > 13:
            st.warning("⚠️ El viaje excede la jornada máxima (13h). Se ha añadido un descanso obligatorio de 11h.")
        else:
            st.success("🟢 El viaje puede completarse en una sola jornada de trabajo.")

            llegada_tras_descanso = r["hora_llegada_dt"] + timedelta(hours=11)
            cambia_dia = llegada_tras_descanso.date() > r["hora_llegada_dt"].date()
            etiqueta = " (día siguiente)" if cambia_dia else ""
            col5.metric("🛌 Llegada + descanso", llegada_tras_descanso.strftime("%H:%M") + etiqueta)

        linea_latlon = [[lat, lng] for lat, lng in r['linea']]
        m = folium.Map(location=linea_latlon[0], zoom_start=6)
        folium.Marker(location=[r['coord_origen'][1], r['coord_origen'][0]], tooltip="📍 Origen").add_to(m)
        for idx, parada in enumerate(r['stops_list']):
            folium.Marker(location=[parada[1], parada[0]], tooltip=f"Parada {idx + 1}").add_to(m)
        folium.Marker(location=[r['coord_destino'][1], r['coord_destino'][0]], tooltip="Destino").add_to(m)
        folium.PolyLine(linea_latlon, color="blue", weight=5).add_to(m)
        st.markdown("### 🗘️ Ruta estimada en mapa:")
        st_folium(m, width=1200, height=500)
