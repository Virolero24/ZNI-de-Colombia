import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ZNI Dashboard", layout="wide")
st.title("⚡ Análisis de Transición Energética Justa")

# URL Directa (Asegúrate de que esta sea la única)
URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/main/datos_procesados.csv"

def load_data():
    # El 'index_col=None' ayuda si el CSV tiene una columna vacía al inicio
    return pd.read_csv(URL, index_col=None)

try:
    df = load_data()
    st.success("✅ ¡Conexión establecida con éxito!")
    
    # Limpieza inmediata de columnas
    df.columns = df.columns.str.strip()
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})

    # --- VISUALIZACIÓN ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Clustering (K-Means)")
        # Verificamos si las columnas existen antes de graficar
        if 'POTENCIA MÁXIMA' in df.columns and 'ENERGÍA ACTIVA' in df.columns:
            color_col = 'CATEGORIA_ZNI' if 'CATEGORIA_ZNI' in df.columns else None
            fig1 = px.scatter(df, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', color=color_col, hover_name='MUNICIPIO')
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Proyecciones a 2028")
        municipios = df['MUNICIPIO'].unique()
        sel = st.multiselect("Municipio:", municipios, default=[municipios[0]])
        fig2 = px.line(df[df['MUNICIPIO'].isin(sel)], x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', markers=True)
        st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error("❌ ERROR TÉCNICO DETECTADO:")
    st.info(f"El error es: {e}")
    st.write("Verifica si puedes abrir este link en tu navegador:", URL)
