import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Título y Estilo
st.set_page_config(page_title="ZNI Dashboard - Ingeniería", layout="wide")
st.title("⚡ Análisis de Transición Energética Justa")

# 2. Carga de datos desde TU repositorio
@st.cache_data
def load_data():
    # Esta URL apunta directamente a tu archivo en el repo Virolero24
    url = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/main/datos_procesados.csv"
    df = pd.read_csv(url)
    # Corrección de columna por si acaso
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})
    return df

try:
    df = load_data()
    st.success("✅ Datos sincronizados con el Notebook de Colab")

    # 3. Mostrar lo que ya calculaste en Colab
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Clustering (K-Means)")
        fig1 = px.scatter(df, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', 
                          color='CATEGORIA_ZNI', hover_name='MUNICIPIO')
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Proyecciones a 2028")
        muni = st.multiselect("Seleccionar Municipio:", df['MUNICIPIO'].unique(), default=['SAN ANDRES'])
        df_plot = df[df['MUNICIPIO'].isin(muni)]
        fig2 = px.line(df_plot, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', markers=True)
        st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error("Esperando a que el Notebook genere el archivo 'datos_procesados.csv' en GitHub.")
