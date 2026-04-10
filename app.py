import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard ZNI Colombia", layout="wide")

# URL del archivo (Asegúrate de que este sea el nombre exacto en tu GitHub)
URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/main/datos_procesados%20(1).csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        # Cargamos el archivo ignorando errores de líneas
        df = pd.read_csv(URL, on_bad_lines='skip')
        
        # Limpieza estándar de columnas
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Localizar la columna del año (manejando 'AÑO SERVICIO' o similares)
        for col in df.columns:
            if 'AÑO' in col or 'ANIO' in col:
                df = df.rename(columns={col: 'YEAR'})
                break
        
        # Conversión segura a números
        df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
        df['ENERGÍA ACTIVA'] = pd.to_numeric(df['ENERGÍA ACTIVA'], errors='coerce')
        
        # Limpieza de nombres de municipios
        df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
        
        # Quitar filas vacías
        df = df.dropna(subset=['YEAR', 'ENERGÍA ACTIVA', 'MUNICIPIO'])
        
        # Agrupar para que no haya líneas verticales
        df = df.groupby(['MUNICIPIO', 'YEAR'], as_index=False)['ENERGÍA ACTIVA'].sum()
        
        return df.sort_values(['MUNICIPIO', 'YEAR'])
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return pd.DataFrame()

# --- INTERFAZ ---
data = load_data()

st.title("⚡ Monitoreo Energético - ZNI Colombia")

if not data.empty:
    # Filtro de Municipios
    municipios = sorted(data['MUNICIPIO'].unique().tolist())
    seleccion = st.multiselect("Selecciona municipios para comparar:", municipios, default=[municipios[0]])

    if seleccion:
        df_filtrado = data[data['MUNICIPIO'].isin(seleccion)]
        
        # Gráfico principal
        fig = px.line(
            df_filtrado, 
            x='YEAR', 
            y='ENERGÍA ACTIVA', 
            color='MUNICIPIO', 
            markers=True,
            title="Histórico de Consumo de Energía",
            labels={'YEAR': 'Año', 'ENERGÍA ACTIVA': 'Energía (kWh)'},
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de datos
        with st.expander("Ver tabla de datos detallada"):
            st.write(df_filtrado)
else:
    st.warning("No se pudieron cargar los datos. Verifica que el archivo existe en el repositorio.")
