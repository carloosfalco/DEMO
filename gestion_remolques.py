if accion == "Entrada a mantenimiento":
    matricula = st.text_input("Introduce matrícula del remolque").strip().upper()
    tipo_mant = st.text_input("Descripción del mantenimiento")

    # Buscar el subtipo automáticamente
    tipo_autom = subtipos[subtipos["matricula"] == matricula]["subtipo"]
    tipo_detectado = tipo_autom.iloc[0] if not tipo_autom.empty else ""

    st.info(f"Tipo detectado: **{tipo_detectado or 'No encontrado'}**")

    if st.button("Registrar entrada"):
        if matricula:
            if matricula not in remolques["matricula"].values:
                nuevo = pd.DataFrame([{
                    "matricula": matricula,
                    "tipo": tipo_detectado,
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
                if tipo_detectado:
                    remolques.loc[remolques["matricula"] == matricula, "tipo"] = tipo_detectado
                guardar_datos(remolques, mantenimientos)
                st.success(f"Remolque {matricula} registrado en mantenimiento.")
            else:
                st.warning("Ese remolque ya está registrado en mantenimiento.")
        else:
            st.warning("Introduce una matrícula válida.")
