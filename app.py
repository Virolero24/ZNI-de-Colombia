import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análisis Energético ZNI", layout="wide")

URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/refs/heads/main/datos_dashboard%20(1).csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(URL, on_bad_lines='skip')
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Identificar columnas clave
        for col in df.columns:
            if 'AÑO' in col or 'ANIO' in col:
                df = df.rename(columns={col: 'YEAR'})
                break
        
        # Conversión numérica limpia
        cols_to_fix = ['YEAR', 'ENERGÍA ACTIVA', 'POTENCIA MÁXIMA']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
        return df.dropna(subset=['YEAR', 'ENERGÍA ACTIVA', 'MUNICIPIO'])
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

data = load_data()

if not data.empty:
    st.title("⚡ Dashboard de Ingeniería ZNI")
    
    # --- FILTROS ---
    municipios = sorted(data['MUNICIPIO'].unique().tolist())
    seleccion = st.multiselect("Seleccionar Municipios para el análisis:", municipios, default=[municipios[0]])
    df_filtrado = data[data['MUNICIPIO'].isin(seleccion)]

    # --- FILA 1: TENDENCIA Y DISPERSIÓN ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Tendencia Histórica")
        fig_line = px.line(df_filtrado, x='YEAR', y='ENERGÍA ACTIVA', color='MUNICIPIO', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.subheader("🎯 Gráfico de Dispersión")
        # Relación entre Potencia y Energía
        if 'POTENCIA MÁXIMA' in df_filtrado.columns:
            fig_scatter = px.scatter(df_filtrado, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', 
                                   color='MUNICIPIO', hover_name='YEAR',
                                   title="Potencia Máxima vs Energía Activa")
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No se encontró la columna de Potencia para la dispersión.")

    st.divider()

    # --- FILA 2: HISTOGRAMA Y CORRELACIÓN ---
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📊 Histograma de Consumo")
        fig_hist = px.histogram(df_filtrado, x='ENERGÍA ACTIVA', nbins=20, 
                               title="Distribución de Energía Activa (kWh)",
                               color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_hist, use_container_width=True)

    with col4:
        st.subheader("🌡️ Matriz de Correlación")
        # Seleccionamos solo columnas numéricas para la matriz
        df_corr = df_filtrado.select_dtypes(include=['float64', 'int64'])
        if not df_corr.empty and len(df_corr.columns) > 1:
            corr = df_corr.corr()
            fig_corr, ax = plt.subplots()
            sns.heatmap(corr, annot=True, cmap='RdYlGn', ax=ax, center=0)
            st.pyplot(fig_corr)
        else:
            st.info("Se necesitan más variables numéricas para la correlación.")

else:
    st.warning("No se encontraron datos. Verifica el archivo en GitHub.")
