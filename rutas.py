import streamlit as st
import requests
import math
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
import flexpolyline

HERE_API_KEY = "XfOePE686kVgu8UfeT8BxvJGAE5bUBipiXdOhD61MwA"

# Inicializar claves en session_state para evitar KeyError
for key in ['route_result', 'origen', 'destino', 'hora_salida']:
    if key not in st.session_state:
        st.session_state[key] = None

def geocode_here(direccion, api_key):
    url = "https://geocode.search.hereapi.com/v1/geocode"
    params = {"q": direccion, "apiKey": api_key, "in": "countryCode:ESP"}
    r = requests.get(url, params=params).json()
    if r.get("items"):
        loc = r["items"][0]["position"]
        return [loc["lng"], loc["lat"]]
    return None

def ruta_camion_here(origen_coord, destino_coord, paradas, api_key):
    url = "https://router.hereapi.com/v8/routes"
    origin = f"{origen_coord[1]},{origen_coord[0]}"
    destination = f"{destino_coord[1]},{destino_coord[0]}"
    via = [f"{p[1]},{p[0]}" for p in paradas]

    params = {
        "transportMode": "truck",
        "origin": origin,
        "destination": destination,
        "return": "polyline,summary",
        "apikey": api_key,
        "truck[height]": "4",
        "truck[weight]": "40000",
        "truck[axleCount]": "4"
    }

    for i, v in enumerate(via):
        params[f"via[{i}]"] = v

    r = requests.get(url, params=params).json()
    return r

def horas_y_minutos(valor_horas):
    horas = int(valor_horas)
    minutos = int(round((valor_horas - horas) * 60))
    return f"{horas}h {minutos:02d}min"

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

    st.title("TMS - Planificador de rutas para camiones")
    origen = st.text_input("📍 Origen", value="Valencia, España")
    destino = st.text_input("🏁 Destino", value="Madrid, España")
    hora_salida_str = st.time_input("🕒 Hora de salida", value=datetime.strptime("08:00", "%H:%M")).strftime("%H:%M")
    stops = st.text_area("➕ Paradas intermedias (una por línea)")

    if st.button("🔍 Calcular Ruta"):
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
        st.session_state['route_result'] = (ruta, coord_origen, coord_destino, stops_list, hora_salida_str)

    if st.session_state.get('route_result'):
        ruta, coord_origen, coord_destino, stops_list, hora_salida_str = st.session_state['route_result']

        if not ruta or "routes" not in ruta:
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
            poly = section.get("polyline")
            if poly:
                coords = flexpolyline.decode(poly)
                for lat, lon in coords:
                    lineas.append([lat, lon])

        if not lineas:
            st.error("❌ No se pudo decodificar ninguna polilínea de la ruta.")
            return

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

        m = folium.Map(location=lineas[0], zoom_start=6)
        folium.Marker(location=[coord_origen[1], coord_origen[0]], tooltip="📍 Origen").add_to(m)
        for idx, parada in enumerate(stops_list):
            folium.Marker(location=[parada[1], parada[0]], tooltip=f"Parada {idx + 1}").add_to(m)
        folium.Marker(location=[coord_destino[1], coord_destino[0]], tooltip="Destino").add_to(m)
        folium.PolyLine(lineas, color="blue", weight=5).add_to(m)

        st.markdown("### 🗘️ Ruta estimada en mapa:")
        st_folium(m, width=1200, height=500)

        st.info("ℹ️ **Nota importante:** La ruta, duración y hora de llegada mostradas son aproximaciones basadas en datos de HERE. Factores reales como tráfico, condiciones meteorológicas, obras o restricciones específicas para camiones pueden alterar significativamente estos valores.")
