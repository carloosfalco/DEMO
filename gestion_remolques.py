if accion == "Entrada a mantenimiento":
    matricula = st.text_input("Introduce matrícula del remolque")
    tipo_mant = st.text_input("Descripción del mantenimiento")

    if st.button("Registrar entrada"):
        if matricula:
            if matricula not in remolques["matricula"].values:
                nuevo = pd.DataFrame([{
                    "matricula": matricula,
                    "tipo": "",
                    "parking": "",
                    "chofer": "",
                    "fecha": "",
                    "estado": "mantenimiento"
                }])
                remolques = pd.concat([remolques, nuevo], ignore_index=True)

            if matricula not in mantenimientos["matricula"].values:
                entrada = pd.DataFrame([{"matricula": matricula, "tipo_mantenimiento": tipo_mant}])
                mantenimientos = pd.concat([mantenimientos, entrada], ignore_index=True)
                remolques.loc[remolques["matricula"] == matricula, "estado"] = "mantenimiento"
                guardar_datos(remolques, mantenimientos)
                st.success(f"Remolque {matricula} registrado en mantenimiento.")
            else:
                st.warning("Ese remolque ya está registrado en mantenimiento.")
        else:
            st.warning("Introduce una matrícula válida.")

elif accion == "Fin de mantenimiento":
    if not mantenimientos.empty:
        matricula = st.selectbox("Selecciona matrícula en taller", mantenimientos["matricula"].unique())
        if st.button("Marcar como disponible"):
            mantenimientos = mantenimientos[mantenimientos["matricula"] != matricula]
            if matricula not in remolques["matricula"].values:
                nuevo = pd.DataFrame([{
                    "matricula": matricula,
                    "tipo": "",
                    "parking": "",
                    "chofer": "",
                    "fecha": datetime.today().strftime('%Y-%m-%d'),
                    "estado": "disponible"
                }])
                remolques = pd.concat([remolques, nuevo], ignore_index=True)
            else:
                remolques.loc[remolques["matricula"] == matricula, "estado"] = "disponible"
                remolques.loc[remolques["matricula"] == matricula, "fecha"] = datetime.today().strftime('%Y-%m-%d')

            guardar_datos(remolques, mantenimientos)
            st.success(f"Remolque {matricula} marcado como disponible.")
    else:
        st.info("No hay remolques en mantenimiento actualmente.")

elif accion == "Asignación a chófer":
    disponibles = remolques[remolques["estado"] == "disponible"]
    if not disponibles.empty:
        matricula = st.selectbox("Selecciona matrícula disponible", disponibles["matricula"])
        chofer = st.text_input("Nombre del chófer")
        if st.button("Asignar remolque"):
            remolques.loc[remolques["matricula"] == matricula, "estado"] = "asignado"
            remolques.loc[remolques["matricula"] == matricula, "chofer"] = chofer
            remolques.loc[remolques["matricula"] == matricula, "fecha"] = datetime.today().strftime('%Y-%m-%d')
            guardar_datos(remolques, mantenimientos)
            st.success(f"Remolque {matricula} asignado a {chofer}.")
    else:
        st.info("No hay remolques disponibles.")
