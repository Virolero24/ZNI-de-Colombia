import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard ZNI - Ingeniería", layout="wide")

URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/main/datos_procesados.csv"

@st.cache_data(ttl=30)
def load_and_clean():
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip()
    
    # 1. Estandarización de nombres y tildes
    df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
    replacements = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    for k, v in replacements.items():
        df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(k, v)
    
    # 2. Manejo de la columna AÑO
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})
    
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce')
    df = df.dropna(subset=['AÑO', 'ENERGÍA ACTIVA'])
    
    # 3. Agrupación segura (evita el error de CATEGORIA_ZNI)
    # Agrupamos solo por los ejes principales para asegurar que la línea sea continua
    columnas_agrupamiento = ['MUNICIPIO', 'AÑO']
    if 'CATEGORIA_ZNI' in df.columns:
        columnas_agrupamiento.append('CATEGORIA_ZNI')
        
    df = df.groupby(columnas_agrupamiento, as_index=False).agg({
        'ENERGÍA ACTIVA': 'sum',
        'POTENCIA MÁXIMA': 'max'
    })
    
    return df.sort_values(['MUNICIPIO', 'AÑO'])

try:
    df = load_and_clean()

    st.title("⚡ Transición Energética Justa - ZNI")
    
    # Métricas de Presentación
    c1, c2, c3 = st.columns(3)
    c1.metric("Municipios Analizados", len(df['MUNICIPIO'].unique()))
    c2.metric("Impacto Estratégico", "70.18%")
    c3.metric("Alcance Temporal", f"{int(df['AÑO'].min())} - {int(df['AÑO'].max())}")

    st.divider()

    # 1. Segmentación con colores por Municipio
    st.subheader("📊 1. Distribución de Demanda Energética")
    fig1 = px.scatter(
        df, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', 
        color='MUNICIPIO', 
        hover_name='MUNICIPIO',
        template="plotly_white",
        title="Relación Potencia vs Energía por Ubicación"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Análisis Histórico y Proyecciones
    st.divider()
    st.subheader("📈 2. Histórico y Proyecciones a 2028")
    
    m_list = sorted(df['MUNICIPIO'].unique())
    # Intentamos seleccionar San Andrés por defecto, si no, el primero de la lista
    default_m = [m for m in ['SAN ANDRES'] if m in m_list] or [m_list[0]]
    
    sel_municipios = st.multiselect("Seleccionar para comparar tendencias:", m_list, default=default_m)
    
    df_plot = df[df['MUNICIPIO'].isin(sel_municipios)]
    
    if not df_plot.empty:
        fig2 = px.line(
            df_plot, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', 
            markers=True, template="plotly_white",
            title="Evolución y Predicción de Energía Activa (kWh)"
        )
        
        # Sombreado de predicción (resalta los años de IA)
        fig2.add_vrect(
            x0=2024.5, x1=2028.5, fillcolor="rgba(46, 204, 113, 0.2)", 
            layer="below", line_width=0,
            annotation_text="ZONA DE PREDICCIÓN IA"
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Por favor, selecciona al menos un municipio para ver la gráfica.")

except Exception as e:
    st.error(f"Se detectó un detalle en los datos: {e}")
    st.info("Asegúrate de que el archivo CSV en GitHub tenga los datos actualizados hasta 2028.")
