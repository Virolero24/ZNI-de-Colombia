import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ZNI Dashboard - Ingeniería", layout="wide")

# URL con el nombre exacto
URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/main/datos_dashboard%20(1).csv"

@st.cache_data(ttl=5)
def load_data():
    # 1. Carga inicial
    df = pd.read_csv(URL)
    
    # 2. Limpieza radical de nombres de columnas
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Si hay columnas duplicadas (ej. dos que se llamen AÑO), las eliminamos
    df = df.loc[:, ~df.columns.duplicated()]
    
    # 3. Forzar el nombre de la columna AÑO (manejando AÑO SERVICIO)
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})
    
    # 4. Asegurarnos de que AÑO y ENERGÍA sean unidimensionales y numéricos
    # Usamos .squeeze() para evitar el error de "not 1-dimensional"
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce')
    df['ENERGÍA ACTIVA'] = pd.to_numeric(df['ENERGÍA ACTIVA'], errors='coerce')
    
    # 5. Limpieza de Municipios
    df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
    remplazos = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    for k, v in remplazos.items():
        df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(k, v)

    # 6. Eliminar filas con errores antes de agrupar
    df = df.dropna(subset=['AÑO', 'ENERGÍA ACTIVA', 'MUNICIPIO'])
    
    # 7. AGRUPACIÓN SEGURA (Aquí se soluciona el error del Grouper)
    # Agrupamos solo por los valores únicos
    df_clean = df.groupby(['MUNICIPIO', 'AÑO'], as_index=False)['ENERGÍA ACTIVA'].sum()
    
    return df_clean.sort_values(['MUNICIPIO', 'AÑO'])

try:
    data = load_data()
    
    st.title("⚡ Transición Energética Justa - ZNI")
    
    if not data.empty:
        # Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("Municipios", len(data['MUNICIPIO'].unique()))
        c2.metric("Impacto Estratégico", "70.18%")
        c3.metric("Alcance", f"{int(data['AÑO'].min())} - {int(data['AÑO'].max())}")

        st.divider()

        # Selector
        municipios = sorted(data['MUNICIPIO'].unique().tolist())
        default_m = [m for m in ['SAN ANDRES'] if m in municipios] or [municipios[0]]
        seleccion = st.multiselect("Seleccionar Municipio:", municipios, default=default_m)

        if seleccion:
            df_plot = data[data['MUNICIPIO'].isin(seleccion)]
            
            # Gráfico de Líneas
            fig = px.line(df_plot, x='AÑO', y='ENERGÍA ACTIVA', color='MUNICIPIO', 
                         markers=True, template="plotly_white", 
                         title="Evolución de Demanda Energética")
            
            # Sombreado de Proyección
            if data['AÑO'].max() >= 2025:
                fig.add_vrect(x0=2024.5, x1=2028.5, fillcolor="rgba(46, 204, 113, 0.2)", 
                             layer="below", line_width=0, annotation_text="PREDICCIÓN IA")
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Ver tabla de datos"):
                st.dataframe(df_plot)
    else:
        st.warning("El archivo se cargó pero está vacío o no tiene el formato correcto.")

except Exception as e:
    st.error(f"Error cargando el Dashboard: {e}")
