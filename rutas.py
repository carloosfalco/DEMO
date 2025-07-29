import streamlit as st
import requests
import math
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from PIL import Image
import polyline

# ⚡ Inserta aquí tu API Key de HERE
HERE_API_KEY = "XfOePE686kVgu8UfeT8BxvJGAE5bUBipiXdOhD61MwA"

# ---------------------- FUNCIONES ----------------------

def geocode_here(direccion, api_key):
    url = "https://geocode.search.hereapi.com/v1/geocode"
    params = {"q": direccion, "apiKey": api_key, "in": "countryCode:ESP"}
    r = requests.get(url, params=params).json()
    if r.get("items"):
        loc = r["items"][0]["position"]
        return [loc["lng"], loc["lat"]]
    return None

def ruta_camion_here(origen_coord, destino_coord, paradas, api_key):
    waypoints = [f"{origen_coord[1]},{origen_coord[0]}" ]  # lat,lng
    for p in paradas:
        waypoints.append(f"{p[1]},{p[0]}")
    waypoints.append(f"{destino_coord[1]},{destino_coord[0]}")

    url = "https://router.hereapi.com/v8/routes"
    params = {
        "transportMode": "truck",
        "origin": waypoints[0],
        "destination": waypoints[-1],
        "return": "polyline,summary",
        "apikey": api_key,
        # HERE requiere cadenas, sin unidades ni decimales flotantes
        "truck[height]": "4",
        "truck[weight]": "40000",
        "truck[axleCount]": "4"
    }

    if len(waypoints) > 2:
        params["via"] = "|".join(waypoints[1:-1])

    r = requests.get(url, params=params).json()
    return r

def horas_y_minutos(valor_horas):
    horas = int(valor_horas)
    minutos = int(round((valor_horas - horas) * 60))
    return f"{horas}h {minutos:02d}min"

# ---------------------- INTERFAZ STREAMLIT ----------------------

def planificador_rutas():
    st.markdown("""
        <style>
            body {background-color: #f5f5f5;}
            .stButton>button {
                background-color: #8D1B2D;
                color: white;
                border-radius: 6px;
                padding: 0.6em 1em;
                border: none;
                font-weight: bold;
            }
            .stButton>button:hover {background-color: #a7283d; color: white;}
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

        coord_origen = geocode_here(origen, HERE_API_KEY)
        coord_destino = geocode_here(destino, HERE_API_KEY)

        stops_list = []
        if stops.strip():
            for parada in stops.strip().split("\n"):
                coord = geocode_here(parada, HERE_API_KEY)
                if coord:
                    stops_list.append(coord)
                else:
                    st.warning(f"❌ No se pudo geolocalizar: {parada}")

        if not coord_origen or not coord_destino:
            st.error("❌ No se pudo geolocalizar el origen o destino.")
            return

        ruta = ruta_camion_here(coord_origen, coord_destino, stops_list, HERE_API_KEY)
        if "routes" not in ruta:
            st.error("❌ Error al calcular la ruta con HERE.")
            st.json(ruta)
            return

        summary = ruta["routes"][0]["sections"][0]["summary"]
        distancia_km = summary["length"] / 1000
        duracion_horas = summary["duration"] / 3600

        descansos = math.floor(duracion_horas / 4.5)
        tiempo_total_h = duracion_horas + descansos * 0.75
        descanso_diario_h = 11 if tiempo_total_h > 13 else 0
        tiempo_total_real_h = tiempo_total_h + descanso_diario_h
        hora_salida = datetime.strptime(hora_salida_str, "%H:%M")
        hora_llegada = hora_salida + timedelta(hours=tiempo_total_real_h)

        tiempo_conduccion_txt = horas_y_minutos(duracion_horas)
        tiempo_total_txt = horas_y_minutos(tiempo_total_h)

        lineas = []
        for section in ruta["routes"][0]["sections"]:
            if "polyline" in section:
                lineas += polyline.decode(section["polyline"])

        st.markdown("### 📊 Datos de la ruta")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🚛 Distancia", f"{distancia_km:.2f} km")
        col2.metric("🕓 Conducción", tiempo_conduccion_txt)
        col3.metric("⏱ Total (con descansos)", tiempo_total_txt)
        col4.metric("📅 Llegada estimada", hora_llegada.strftime("%H:%M"))

        if tiempo_total_real_h > 13:
            st.warning("⚠️ El viaje excede la jornada máxima (13h). Se ha añadido un descanso obligatorio de 11h.")
        else:
            st.success("🟢 El viaje puede completarse en una sola jornada de trabajo.")
            llegada_tras_descanso = hora_llegada + timedelta(hours=11)
            etiqueta = " (día siguiente)" if llegada_tras_descanso.date() > hora_llegada.date() else ""
            col5.metric("🛌 Llegada + descanso", llegada_tras_descanso.strftime("%H:%M") + etiqueta)

        linea_latlon = [[p[0], p[1]] for p in lineas]
        m = folium.Map(location=linea_latlon[0], zoom_start=6)
        folium.Marker(location=[coord_origen[1], coord_origen[0]], tooltip="📍 Origen").add_to(m)
        for idx, parada in enumerate(stops_list):
            folium.Marker(location=[parada[1], parada[0]], tooltip=f"Parada {idx + 1}").add_to(m)
        folium.Marker(location=[coord_destino[1], coord_destino[0]], tooltip="Destino").add_to(m)
        folium.PolyLine(linea_latlon, color="blue", weight=5).add_to(m)

        st.markdown("### 🗘️ Ruta estimada en mapa:")
        st_folium(m, width=1200, height=500)

        st.info("ℹ️ **Nota importante:** La ruta, duración y hora de llegada mostradas son aproximaciones basadas en datos de HERE. "
                "Factores reales como tráfico, condiciones meteorológicas, obras o restricciones específicas para camiones pueden alterar significativamente estos valores.")
