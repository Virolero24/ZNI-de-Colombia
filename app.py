import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard ZNI - Ingeniería", layout="wide")

URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/refs/heads/main/datos_procesados%20(1).csv"

@st.cache_data(ttl=10)
def load_and_clean():
    # Carga el archivo ignorando errores de líneas mal formadas
    df = pd.read_csv(URL, on_bad_lines='skip')
    
    # Limpieza de columnas
    df.columns = df.columns.str.strip()
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})
    
    # Limpieza de Municipios (Elimina tildes y duplicados)
    df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
    remplazos = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    for k, v in remplazos.items():
        df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(k, v)
    
    # Conversión segura a números (Evita el error de 'arg must be a list')
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce')
    df['ENERGÍA ACTIVA'] = pd.to_numeric(df['ENERGÍA ACTIVA'], errors='coerce')
    
    # Quitamos filas que no tengan año o energía
    df = df.dropna(subset=['AÑO', 'ENERGÍA ACTIVA'])
    
    # Agrupación para evitar líneas verticales duplicadas
    cols_group = ['MUNICIPIO', 'AÑO']
    if 'CATEGORIA_ZNI' in df.columns:
        cols_group.append('CATEGORIA_ZNI')
        
    df = df.groupby(cols_group, as_index=False).agg({
        'ENERGÍA ACTIVA': 'sum',
        'POTENCIA MÁXIMA': 'max'
    })
    
    return df.sort_values(['MUNICIPIO', 'AÑO'])

try:
    df = load_and_clean()
    st.title("⚡ Transición Energética Justa - ZNI")
    
    # --- MÉTRICAS ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Municipios", len(df['MUNICIPIO'].unique()))
    m2.metric("Impacto Estratégico", "70.18%")
    m3.metric("Máximo Año Detectado", int(df['AÑO'].max()))

    st.divider()

    # --- 1. SEGMENTACIÓN ---
    st.subheader("📊 1. Distribución de Demanda por Municipio")
    lista_m = sorted(df['MUNICIPIO'].unique().tolist())
    
    sel_scatter = st.multiselect("Filtrar para dispersión:", lista_m, default=lista_m, key="s1")
    
    df_s = df[df['MUNICIPIO'].isin(sel_scatter)]
    if not df_s.empty:
        fig1 = px.scatter(df_s, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', color='MUNICIPIO', 
                         hover_name='MUNICIPIO', template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)

    # --- 2. HISTÓRICO Y PREDICCIONES ---
    st.divider()
    st.subheader("📈 2. Evolución Histórica y Proyección IA (2025-2028)")
    
    # Pre-seleccionamos San Andres si existe
    default_l = [m for m in ['SAN ANDRES'] if m in lista_m] or [lista_m[0]]
    sel_line = st.multiselect("Seleccionar para tendencia:", lista_m, default=default_l, key="l1")
    
    df_l = df[df['MUNICIPIO'].isin(sel_line)]
    
    if not df_l.empty:
        fig2 = px.line(df_l, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', markers=True, 
                       template="plotly_white", title="Tendencia de Energía Activa")
        
        # Sombreado de zona de predicción
        fig2.add_vrect(x0=2024.5, x1=2028.5, fillcolor="rgba(46, 204, 113, 0.2)", 
                       layer="below", line_width=0, annotation_text="PREDICCIÓN IA")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Selecciona un municipio.")

except Exception as e:
    st.error(f"Error detectado: {e}")
    st.info("Revisa que el archivo CSV tenga los datos de predicción correctamente.")
