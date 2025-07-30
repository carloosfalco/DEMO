import streamlit as st
import requests
import math
from datetime import datetime, timedelta
import flexpolyline
import pydeck as pdk

HERE_API_KEY = "XfOePE686kVgu8UfeT8BxvJGAE5bUBipiXdOhD61MwA"

# Inicializar claves en session_state
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

    col1, col2, col3 = st.columns(3)
    with col1:
        origen = st.text_input("📍 Origen", value="Valencia, España")
    with col2:
        destino = st.text_input("🏁 Destino", value="Madrid, España")
    with col3:
        hora_salida_str = st.time_input("🕒 Hora", value=datetime.strptime("08:00", "%H:%M")).strftime("%H:%M")

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

        latlngs = [[lat, lon] for lat, lon in lineas]
        layers = [pdk.Layer(
            "PathLayer",
            data=[{"path": latlngs, "name": "Ruta"}],
            get_path="path",
            get_color=[0, 0, 255],
            width_scale=10,
            width_min_pixels=3
        )]

        # Añadir marcadores para origen, destino y paradas
        markers_data = [{"lat": coord_origen[1], "lon": coord_origen[0], "color": [0,255,0]},
                        {"lat": coord_destino[1], "lon": coord_destino[0], "color": [255,0,0]}]
        for stop in stops_list:
            markers_data.append({"lat": stop[1], "lon": stop[0], "color": [255,165,0]})

        marker_layer = pdk.Layer(
            "ScatterplotLayer",
            data=markers_data,
            get_position='[lon, lat]',
            get_fill_color='color',
            get_radius=5000
        )
        layers.append(marker_layer)

        view_state = pdk.ViewState(
            latitude=lineas[0][0],
            longitude=lineas[0][1],
            zoom=6,
            pitch=0
        )

        st.markdown("### 🗘️ Ruta estimada en mapa:")
        st.pydeck_chart(pdk.Deck(map_style="road", layers=layers, initial_view_state=view_state))

        st.info("ℹ️ **Nota importante:** La ruta, duración y hora de llegada mostradas son aproximaciones basadas en datos de HERE. Factores reales como tráfico, condiciones meteorológicas, obras o restricciones específicas para camiones pueden alterar significativamente estos valores.")
