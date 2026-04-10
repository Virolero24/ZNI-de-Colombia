import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard ZNI - Ingeniería", layout="wide")

URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/refs/heads/main/datos_procesados.csv"

@st.cache_data(ttl=30)
def load_and_clean():
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip()
    
    # Estandarización de nombres y tildes
    df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
    replacements = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    for k, v in replacements.items():
        df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(k, v)
    
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})
    
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce')
    df = df.dropna(subset=['AÑO', 'ENERGÍA ACTIVA'])
    
    # IMPORTANTE: Agrupar para evitar líneas verticales duplicadas
    df = df.groupby(['MUNICIPIO', 'AÑO', 'CATEGORIA_ZNI'], as_index=False).agg({
        'ENERGÍA ACTIVA': 'sum',
        'POTENCIA MÁXIMA': 'max'
    })
    
    return df.sort_values(['MUNICIPIO', 'AÑO'])

try:
    df = load_and_clean()

    st.title("⚡ Transición Energética Justa - ZNI")
    
    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Municipios", len(df['MUNICIPIO'].unique()))
    c2.metric("Impacto Estratégico", "70.18%")
    c3.metric("Alcance", f"{int(df['AÑO'].min())} - {int(df['AÑO'].max())}")

    st.divider()

    # 1. Segmentación con colores por Municipio
    st.subheader("📊 1. Segmentación de Demanda por Municipio")
    fig1 = px.scatter(
        df, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', 
        color='MUNICIPIO', # Ahora cada municipio tiene su color
        hover_name='MUNICIPIO',
        template="plotly_white",
        title="Relación Potencia vs Energía por Ubicación"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Análisis Histórico y Proyecciones (Líneas limpias)
    st.divider()
    st.subheader("📈 2. Histórico y Proyecciones a 2028")
    
    m_list = sorted(df['MUNICIPIO'].unique())
    sel_municipios = st.multiselect("Seleccionar para comparar:", m_list, default=[m_list[0]])
    
    df_plot = df[df['MUNICIPIO'].isin(sel_municipios)]
    
    if not df_plot.empty:
        # Gráfico de líneas sin duplicados verticales
        fig2 = px.line(
            df_plot, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', 
            markers=True, template="plotly_white",
            title="Evolución de Energía Activa"
        )
        
        # Sombreado de predicción
        fig2.add_vrect(
            x0=2024.5, x1=2028.5, fillcolor="rgba(46, 204, 113, 0.2)", 
            layer="below", line_width=0,
            annotation_text="PREDICCIÓN IA"
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Selecciona un municipio.")

except Exception as e:
    st.error(f"Error técnico: {e}")
