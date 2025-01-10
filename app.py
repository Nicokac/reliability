import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import altair as alt
import platform

# Configurar el menú de navegación
st.sidebar.title("Menú")
app_mode = st.sidebar.selectbox("Selecciona una funcionalidad", ["Consulta Historian", "Calcular cajas físicas"])

if app_mode == "Consulta Historian":
    # Funcionalidad: Consulta Historian
    st.title("Consulta Historian")

    # Entrada para la URL
    url = st.text_input("Ingrese la URL de consulta", value="http://kofaralcmes01.sa.kof.ccf/historian.asp?id=ar00_env_LI03_Nom_Spd&d=1&g=100&i=&f=&t=h")

    # Botón para cargar datos
    if st.button("Consultar"):
        if url:
            try:
                # Realizar solicitud HTTP a la URL
                response = requests.get(url)
                response.raise_for_status()

                # Parsear el contenido HTML
                soup = BeautifulSoup(response.content, "html.parser")

                # Extraer los datos de la tabla
                table = soup.find("table", {"id": "datos"})
                if table:
                    rows = table.find_all("tr")
                    data = []

                    # Procesar filas de la tabla
                    for row in rows[1:]:  # Ignorar el encabezado
                        cols = row.find_all("td")
                        data.append([col.text.strip() for col in cols])

                    # Mostrar datos en una tabla
                    st.subheader("Datos obtenidos")
                    st.write(f"Se encontraron {len(data)} registros.")
                    st.table(data)

                else:
                    st.error("No se encontró la tabla de datos en la URL proporcionada.")

            except Exception as e:
                st.error(f"Error al consultar la URL: {e}")
        else:
            st.warning("Por favor, ingrese una URL válida.")

    # Gráfico interactivo
    if "data" in locals() and data:
        # Crear DataFrame con los datos extraídos
        df = pd.DataFrame(data, columns=["valor", "minimo", "maximo", "stamp"])

        # Convertir columnas a tipos correctos
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        df["minimo"] = pd.to_numeric(df["minimo"], errors="coerce")
        df["maximo"] = pd.to_numeric(df["maximo"], errors="coerce")
        df["stamp"] = pd.to_datetime(df["stamp"], errors="coerce")

        # Mostrar gráfico interactivo
        st.subheader("Gráfico de valores")
        chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x="stamp:T",
                y="valor:Q",
                tooltip=["stamp", "valor", "minimo", "maximo"]
            )
            .properties(width=700, height=400)
        )
        st.altair_chart(chart, use_container_width=True)

elif app_mode == "Calcular cajas físicas":
    # Funcionalidad: Calcular cajas físicas
    st.title("Calcular cajas físicas")
    st.markdown("Esta herramienta calcula las cajas físicas a partir de cajas unitarias, formato botella y empaque.")

# Constantes
min_sku = 0.237  # float
max_sku = 3  # int originalmente, lo convertimos a float donde se usa
cons = 5.678

# Entradas del usuario
st.sidebar.header("Parámetros de entrada")
cajas_unitarias = st.sidebar.number_input("Cantidad de cajas unitarias", min_value=1, value=1, step=1)
sku = st.sidebar.number_input(
    "Formato botella (litros)", 
    min_value=float(min_sku),  # Convertir a float
    max_value=float(max_sku),  # Convertir a float
    value=0.5, 
    step=0.1
)
empaque = st.sidebar.number_input("Empaque (cantidad de botellas)", min_value=1, value=6, step=1)

# Validación de entradas
if sku < min_sku or sku > max_sku:
    st.error(f"El SKU debe estar entre {min_sku} y {max_sku} litros.")
else:
    # Cálculo de cajas físicas
    lts_bebida = cajas_unitarias * cons
    cant_botellas = lts_bebida / sku
    cajas_fisicas = cant_botellas / empaque

    # Mostrar resultado
    st.subheader("Resultado")
    st.write(f"Cantidad de cajas físicas: **{cajas_fisicas:.2f}**")


    # Información adicional
    st.sidebar.header("Información")
    st.sidebar.markdown(
        f"""
        **Versión del proyecto**: 1.0  
        **Versión de Python**: {platform.python_version()}  
        **Creador**: Nicolás Kachuk  

        **Enlaces**:  
        - [GitHub](https://github.com/Nicokac)  
        - [LinkedIn](https://www.linkedin.com/in/nicolaskachuk)
        """
    )
