import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(
    page_title="Dashboard Energético ZNI Colombia",
    page_icon="⚡",
    layout="wide"
)

# Estilo personalizado para mejorar la apariencia
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Carga de datos (Usando la URL de tu GitHub)
@st.cache_data # Esto hace que la app sea mucho más rápida
def load_data():
    # REEMPLAZA ESTA URL con la dirección "Raw" de tu archivo en GitHub
    url = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/refs/heads/main/datos_finales_zni.csv"
    data = pd.read_csv(url)
    # Aseguramos que los nombres de columnas no tengan espacios extras
    data.columns = data.columns.str.strip()
    return data

try:
    df = load_data()

    # 3. Título y Encabezado
    st.title("⚡ Diagnóstico y Proyección Energética ZNI 2028")
    st.markdown("Análisis de datos para la **Transición Energética Justa** mediante Machine Learning.")
    st.divider()

    # 4. Barra Lateral (Filtros)
    st.sidebar.header("🔍 Filtros de Análisis")
    
    # Selección de municipios con valores predeterminados para evitar el error de "vacío"
    municipios_disponibles = sorted(df['MUNICIPIO'].unique())
    nodos_criticos = [m for m in ['SAN ANDRES', 'LETICIA', 'PUERTO CARREÑO'] if m in municipios_disponibles]
    
    municipio_search = st.sidebar.multiselect(
        "Seleccione Municipios para comparar:",
        options=municipios_disponibles,
        default=nodos_criticos if nodos_criticos else [municipios_disponibles[0]]
    )

    # 5. KPIs Principales (Métricas)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_energia = df['ENERGÍA ACTIVA'].sum()
        st.metric("Consumo Total Histórico", f"{total_energia:,.0f} kWh")
    
    with col2:
        # Cálculo del impacto del Top 3 (Dato clave de tu informe)
        top3 = ['SAN ANDRES', 'LETICIA', 'PUERTO CARREÑO']
        consumo_top3 = df[df['MUNICIPIO'].isin(top3)]['ENERGÍA ACTIVA'].sum()
        porcentaje_top3 = (consumo_top3 / total_energia) * 100
        st.metric("Concentración Top 3", f"{porcentaje_top3:.2f}%", delta="Crítico")
        
    with col3:
        st.metric("Horizonte de Proyección", "Año 2028", delta="Simulado")

    st.divider()

    # 6. Visualizaciones principales
    tab1, tab2 = st.tabs(["📊 Segmentación (Clusters)", "📈 Proyecciones 2028"])

    with tab1:
        st.subheader("Clasificación de Sistemas por K-Means")
        # Gráfico de dispersión para ver los clusters
        fig_clusters = px.scatter(
            df, 
            x='POTENCIA MÁXIMA', 
            y='ENERGÍA ACTIVA', 
            color='CATEGORIA_ZNI',
            hover_name='MUNICIPIO',
            title="Distribución de Municipios por Eficiencia y Demanda",
            color_continuous_scale=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_clusters, use_container_width=True)

    with tab2:
        st.subheader("Tendencia de Crecimiento Proyectada")
        
        # FILTRADO DE DATOS (Aquí evitamos el ValueError)
        df_filtrado = df[df['MUNICIPIO'].isin(municipio_search)]

        if not df_filtrado.empty:
            fig_line = px.line(
                df_filtrado, 
                x='AÑO', 
                y='ENERGÍA ACTIVA', 
                color='MUNICIPIO',
                markers=True,
                title="Evolución y Proyección de Energía Activa",
                template="plotly_white"
            )
            fig_line.update_layout(xaxis_title="Año", yaxis_title="Energía (kWh)")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("⚠️ Selecciona al menos un municipio en la barra lateral para visualizar la tendencia.")

    # 7. Sección de datos brutos (Opcional)
    with st.expander("Ver base de datos procesada"):
        st.write(df)

except Exception as e:
    st.error(f"Error al cargar la aplicación: {e}")
    st.info("Asegúrate de que la URL de GitHub sea correcta y el archivo tenga las columnas: MUNICIPIO, AÑO, ENERGÍA ACTIVA, POTENCIA MÁXIMA y CATEGORIA_ZNI.")

# Pie de página
st.markdown("---")
st.caption("Proyecto desarrollado por Verónica - Ingeniería Mecánica | Pereira, Colombia")
