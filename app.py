import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página profesional
st.set_page_config(page_title="Dashboard ZNI - Ingeniería", layout="wide", initial_sidebar_state="collapsed")

# Estilo personalizado para las métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 30px; color: #2E86C1; }
    [data-testid="stMetricLabel"] { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# URL de los datos
URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/main/datos_procesados.csv"

@st.cache_data(ttl=60)
def load_and_clean():
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip()
    
    # Estandarización de nombres y tildes (Adiós al error de San Andrés)
    df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
    replacements = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    for k, v in replacements.items():
        df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(k, v)
    
    # Manejo de fechas
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce')
    df = df.dropna(subset=['AÑO', 'ENERGÍA ACTIVA']).sort_values(['MUNICIPIO', 'AÑO'])
    
    return df

try:
    df = load_and_clean()

    # --- ENCABEZADO DE PRESENTACIÓN ---
    st.title("⚡ Transición Energética Justa en Zonas No Interconectadas (ZNI)")
    st.markdown("#### Análisis de Datos y Proyecciones de Demanda Mediante IA")
    
    # --- MÉTRICAS CLAVE (Tus hallazgos de ingeniería) ---
    st.divider()
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Municipios Analizados", f"{len(df['MUNICIPIO'].unique())}")
    with kpi2:
        st.metric("Horizonte de Datos", f"{int(df['AÑO'].min())} - {int(df['AÑO'].max())}")
    with kpi3:
        # Tu dato clave de impacto estratégico
        st.metric("Impacto Estratégico", "70.18%", help="Impacto de los 3 municipios principales en la demanda total")
    with kpi4:
        st.metric("Modelo de IA", "Linear/Tree", help="Modelo entrenado para proyecciones a 2028")

    # --- SECCIÓN 1: CLUSTERING (Segmentación) ---
    st.divider()
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📊 1. Segmentación de Demanda (K-Means)")
        color_col = 'CATEGORIA_ZNI' if 'CATEGORIA_ZNI' in df.columns else None
        fig_scatter = px.scatter(
            df, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', color=color_col,
            hover_name='MUNICIPIO', template="plotly_white",
            labels={'POTENCIA MÁXIMA': 'Potencia (kW)', 'ENERGÍA ACTIVA': 'Energía (kWh)'},
            color_continuous_scale=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col_right:
        st.info("""
        **Interpretación de Clusters:**
        El algoritmo identifica grupos de municipios con perfiles de consumo similares. 
        Esto permite priorizar la infraestructura en las zonas con mayor demanda de potencia 
        para una transición energética eficiente.
        """)

    # --- SECCIÓN 2: PROYECCIONES ---
    st.divider()
    st.subheader("📈 2. Análisis Histórico y Proyecciones a 2028")
    
    m_list = sorted(df['MUNICIPIO'].unique())
    # Pre-seleccionar San Andrés para que la gráfica no inicie vacía
    defaults = [m for m in ['SAN ANDRES', 'LETICIA'] if m in m_list]
    if not defaults: defaults = [m_list[0]]
    
    sel_municipios = st.multiselect("Selecciona municipios para comparar tendencias:", m_list, default=defaults)
    
    df_plot = df[df['MUNICIPIO'].isin(sel_municipios)]
    
    if not df_plot.empty:
        fig_line = px.line(
            df_plot, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', markers=True,
            title="Evolución de Energía Activa (Histórico + Proyección)",
            template="plotly_white",
            labels={'ENERGÍA ACTIVA': 'Energía Activa (kWh)', 'AÑO': 'Año'}
        )
        
        # Sombreado elegante para la zona de predicción (IA)
        fig_line.add_vrect(
            x0=2024.5, x1=2028.5, fillcolor="#2ECC71", opacity=0.15, 
            layer="below", line_width=0,
            annotation_text="PROYECCIÓN IA (2025-2028)", annotation_position="top left",
            annotation_font_color="#27AE60"
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Selecciona al menos un municipio para visualizar la tendencia.")

except Exception as e:
    st.error("Error al cargar los datos procesados.")
    st.info(f"Detalle técnico: {e}")
