import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Traer los datos ya procesados por el Colab
@st.cache_data
def load_processed_data():
    # USAMOS LA URL RAW DEL ARCHIVO QUE GENERÓ TU COLAB
    url = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/refs/heads/main/TransicionEnergetica.ipynb"
    return pd.read_csv(url)

df = load_processed_data()

st.title("⚡ Dashboard de Transición Energética")

# 2. Mostrar los Clusters (Que ya vienen listos del Colab)
st.subheader("Segmentación de Municipios (K-Means)")
fig1 = px.scatter(df, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', color='CATEGORIA_ZNI', hover_name='MUNICIPIO')
st.plotly_chart(fig1)

# 3. Mostrar la Proyección (Que ya viene lista del Colab)
st.subheader("Proyección de Demanda a 2028")
municipios = st.multiselect("Selecciona Municipios:", df['MUNICIPIO'].unique(), default=['SAN ANDRES', 'LETICIA'])

df_plot = df[df['MUNICIPIO'].isin(municipios)]

# Simplemente graficamos lo que ya existe en el CSV
fig2 = px.line(df_plot, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', markers=True)
st.plotly_chart(fig2)
