import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard ZNI - Ingeniería", layout="wide")

URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/refs/heads/main/datos_procesados%20(1).csv"

@st.cache_data(ttl=10) # Cache muy corto para ver cambios rápidos
def load_and_clean():
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip()
    
    # Estandarización de nombres
    df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
    replacements = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    for k, v in replacements.items():
        df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(k, v)
    
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})
    
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce')
    df = df.dropna(subset=['AÑO', 'ENERGÍA ACTIVA'])
    
    # Agrupación para evitar líneas verticales
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
    
    # --- MÉTRICAS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Municipios Analizados", len(df['MUNICIPIO'].unique()))
    c2.metric("Impacto Estratégico", "70.18%")
    c3.metric("Último Año en Datos", int(df['AÑO'].max()))

    st.divider()

    # --- 1. SEGMENTACIÓN CON FILTRO ---
    st.subheader("📊 1. Distribución de Demanda por Municipio")
    m_list = sorted(df['MUNICIPIO'].unique())
    
    # Selector para el primer gráfico
    sel_scatter = st.multiselect("Filtrar municipios para el análisis de dispersión:", m_list, default=m_list, key="scatter_sel")
    
    df_scatter = df[df['MUNICIPIO'].isin(sel_scatter)]
    
    fig1 = px.scatter(
        df_scatter, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', 
        color='MUNICIPIO', hover_name='MUNICIPIO',
        template="plotly_white",
        title="Relación Potencia vs Energía (Selección Personalizada)"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- 2. HISTÓRICO Y PREDICCIONES ---
    st.divider()
    st.subheader("📈 2. Evolución Histórica y Proyección IA a 2028")
    
    # Selector para el segundo gráfico
    sel_line = st.multiselect("Seleccionar municipios para ver tendencia y predicción:", m_list, default=[m_list[0]], key="line_sel")
    
    df_plot = df[df['MUNICIPIO'].isin(sel_line)]
    
    if not df_plot.empty:
        fig2 = px.line(
            df_plot, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', 
            markers=True, template="plotly_white",
            title="Consumo Energético: Pasado y Futuro"
        )
        
        # Sombreado de zona de predicción
        fig2.add_vrect(
            x0=2024.5, x1=2028.5, fillcolor="rgba(46, 204, 113, 0.2)", 
            layer="below", line_width=0,
            annotation_text="PREDICCIÓN MODELO IA"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Selecciona un municipio para visualizar la línea de tiempo.")

except Exception as e:
    st.error(f"Error de configuración: {e}")
