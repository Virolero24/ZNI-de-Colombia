import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Energético ZNI", layout="wide")

st.title("Diagnóstico y Proyección Energética ZNI 2028")
st.markdown("Análisis interactivo para la Transición Energética Justa en Colombia")

# 1. Carga de datos (usando tu CSV procesado)
df = pd.read_csv('datos_finales_zni.csv')

# 2. Barra Lateral de Filtros
municipio_search = st.sidebar.multiselect("Seleccionar Municipios:", options=df['MUNICIPIO'].unique(), default=['SAN ANDRES', 'LETICIA'])

# 3. Métricas de Impacto (El dato del 70.18%)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Concentración Top 3", "70.18%", delta="Crítico")
with col2:
    st.metric("Consumo Promedio", f"{df['ENERGÍA ACTIVA'].mean():.2f} kWh")
with col3:
    st.metric("Meta 2028", "Transición 100%")

# 4. Gráfico Interactivo de Clusters
st.subheader("Segmentación por Inteligencia Artificial (K-Means)")
fig_cluster = px.scatter(df, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', color='CATEGORIA_ZNI', 
                 hover_name='MUNICIPIO', title="Grupos de Consumo Identificados")
st.plotly_chart(fig_cluster, use_container_width=True)

# 5. Proyección Interactiva
st.subheader("Tendencia de Crecimiento Individual")
df_filtrado = df[df['MUNICIPIO'].isin(municipio_search)]
fig_line = px.line(df_filtrado, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', markers=True)
st.plotly_chart(fig_line, use_container_width=True)
