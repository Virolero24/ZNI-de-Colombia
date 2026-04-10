import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ZNI Dashboard - Ingeniería", layout="wide")

# URL con el nombre exacto que me indicaste
URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/refs/heads/main/datos_dashboard%20(1).csv"

@st.cache_data(ttl=5)
def load_data():
    # 1. Carga inicial
    df = pd.read_csv(URL)
    
    # 2. Limpieza de nombres de columnas
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Manejar el nombre "AÑO SERVICIO"
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})
    elif 'AÑO' not in df.columns:
        # Si no la encuentra, busca una columna que contenga "AÑO"
        for col in df.columns:
            if 'AÑO' in col:
                df = df.rename(columns={col: 'AÑO'})
                break

    # 3. CONVERSIÓN FORZADA (Soluciona el error 'arg must be a list')
    # Convertimos los valores a una lista plana de Python antes de pasarlos a numérico
    df['AÑO'] = pd.to_numeric(list(df['AÑO']), errors='coerce')
    df['ENERGÍA ACTIVA'] = pd.to_numeric(list(df['ENERGÍA ACTIVA']), errors='coerce')
    
    # 4. Limpieza de Municipios (Quitar tildes y espacios)
    df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
    remplazos = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    for k, v in remplazos.items():
        df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(k, v)

    # 5. Quitar datos incompletos
    df = df.dropna(subset=['AÑO', 'ENERGÍA ACTIVA', 'MUNICIPIO'])
    
    # 6. Agrupación para evitar líneas duplicadas
    df = df.groupby(['MUNICIPIO', 'AÑO'], as_index=False)['ENERGÍA ACTIVA'].sum()
    
    return df.sort_values(['MUNICIPIO', 'AÑO'])

try:
    data = load_data()
    
    st.title("⚡ Transición Energética Justa - ZNI")
    
    # Métricas clave
    c1, c2, c3 = st.columns(3)
    c1.metric("Municipios", len(data['MUNICIPIO'].unique()))
    c2.metric("Impacto Estratégico", "70.18%")
    c3.metric("Alcance Máximo", int(data['AÑO'].max()))

    st.divider()

    # Selector de Municipios
    municipios = sorted(data['MUNICIPIO'].unique().tolist())
    # Pre-seleccionar San Andres si existe, sino el primero
    default_sel = [m for m in ['SAN ANDRES'] if m in municipios] or [municipios[0]]
    seleccion = st.multiselect("Seleccionar Municipio:", municipios, default=default_sel)

    if seleccion:
        df_filtrado = data[data['MUNICIPIO'].isin(seleccion)]
        
        # Gráfico de Líneas
        fig = px.line(df_filtrado, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', 
                     markers=True, template="plotly_white")
        
        # Sombrear la zona de proyecciones
        if data['AÑO'].max() >= 2025:
            fig.add_vrect(x0=2024.5, x1=2028.5, fillcolor="rgba(46, 204, 113, 0.2)", 
                         layer="below", line_width=0, annotation_text="PREDICCIÓN IA")
            
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de Barras para comparar el total proyectado
        st.subheader("Comparativa de Energía por Municipio")
        fig_bar = px.bar(df_filtrado, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"Error cargando el Dashboard: {e}")
    st.info("Verifica que el archivo 'datos_dashboard (1).csv' esté en tu repositorio.")

except Exception as e:
    st.error(f"Error detectado: {e}")
    st.info("Revisa que el archivo CSV tenga los datos de predicción correctamente.")
