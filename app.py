import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración técnica de la interfaz
st.set_page_config(page_title="ZNI Colombia - Dashboard", layout="wide")

# Estilo de encabezado
st.title("⚡ Análisis de Transición Energética Justa")
st.markdown("### Visualización de Datos Históricos y Predicciones (2025-2028)")

# Conexión directa a los datos de tu repositorio
URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/main/datos_procesados.csv"

@st.cache_data(ttl=30)
def load_data():
    # Carga y limpieza inmediata
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip()
    
    # Estandarización de columna AÑO
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})
    
    # Conversión a numérico para asegurar el orden cronológico en la gráfica
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce')
    df = df.dropna(subset=['AÑO', 'ENERGÍA ACTIVA'])
    df = df.sort_values('AÑO')
    
    return df

try:
    df = load_data()

    # --- MÉTRICAS DE IMPACTO (Resultados de tu análisis en Colab) ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Municipios en Análisis", len(df['MUNICIPIO'].unique()))
    with m2:
        st.metric("Horizonte Temporal", f"{int(df['AÑO'].min())} - {int(df['AÑO'].max())}")
    with m3:
        # Valor del impacto estratégico identificado en tu proyecto
        st.metric("Impacto Estratégico (Top 3)", "70.18%")

    st.divider()

    # --- SECCIÓN 1: CLUSTERING ---
    st.subheader("1. Segmentación de Consumo (Clusters K-Means)")
    
    # Identificación dinámica de la columna de clusters
    color_col = 'CATEGORIA_ZNI' if 'CATEGORIA_ZNI' in df.columns else None
    
    fig_scatter = px.scatter(
        df, 
        x='POTENCIA MÁXIMA', 
        y='ENERGÍA ACTIVA', 
        color=color_col,
        hover_name='MUNICIPIO',
        title="Clasificación de Municipios según Demanda y Potencia",
        template="plotly_white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- SECCIÓN 2: PROYECCIONES ---
    st.subheader("2. Evolución y Proyección de Demanda a 2028")
    
    municipios_lista = sorted(df['MUNICIPIO'].unique())
    # Selección por defecto: San Andrés y Leticia (o el primero de la lista)
    defaults = [m for m in ['SAN ANDRES', 'LETICIA'] if m in municipios_lista]
    if not defaults: defaults = [municipios_lista[0]]

    seleccion = st.multiselect("Selecciona Municipios para ver proyecciones:", municipios_lista, default=defaults)

    df_plot = df[df['MUNICIPIO'].isin(seleccion)]

    if not df_plot.empty:
        fig_line = px.line(
            df_plot, 
            x='AÑO', 
            y='ENERGÍA ACTIVA', 
            color='MUNICIPIO',
            markers=True,
            title="Histórico de Consumo + Proyecciones de IA",
            labels={'ENERGÍA ACTIVA': 'Energía Activa (kWh)', 'AÑO': 'Año'}
        )
        
        # Sombreado visual para separar el pasado del futuro (2025-2028)
        fig_line.add_vrect(
            x0=2024.5, x1=2028.5, 
            fillcolor="green", opacity=0.1, 
            layer="below", line_width=0,
            annotation_text="PROYECCIÓN IA", annotation_position="top left"
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Selecciona al menos un municipio para visualizar la tendencia.")

except Exception as e:
    st.error("Error al cargar los datos procesados.")
    st.code(f"Error: {e}")
