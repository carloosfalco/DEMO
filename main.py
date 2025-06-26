from gestion_remolques import gestion_remolques  # Importaremos este módulo nuevo

def main():
    st.set_page_config(page_title="Virosque TMS", page_icon="🚛", layout="wide")

    st.sidebar.title("📂 Menú")
    seleccion = st.sidebar.radio("Selecciona una opción", [
        "Planificador de rutas",
        "Orden de carga",
        "Gestión de remolques"  # Nuevo
    ])

    if seleccion == "Planificador de rutas":
        planificador_rutas()
    elif seleccion == "Orden de carga":
        generar_orden_carga_manual()
    elif seleccion == "Gestión de remolques":
        gestion_remolques()  # Nuevo
