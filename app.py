import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Análisis ZNI - Ingeniería", layout="wide")

URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/refs/heads/main/datos_dashboard%20(1).csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(URL, on_bad_lines='skip')
    df.columns = [str(c).strip().upper() for c in df.columns]
    for col in df.columns:
        if 'AÑO' in col or 'ANIO' in col:
            df = df.rename(columns={col: 'YEAR'})
            break
    cols_num = ['YEAR', 'ENERGÍA ACTIVA', 'POTENCIA MÁXIMA']
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
    return df.dropna(subset=['YEAR', 'ENERGÍA ACTIVA', 'MUNICIPIO'])

data = load_data()

if not data.empty:
    st.title("📊 Reporte de Ingeniería: Datos ZNI")
    st.markdown("---")

    # --- FILTROS LATERALES PARA NO OCUPAR ESPACIO ---
    with st.sidebar:
        st.header("Configuración")
        municipios = sorted(data['MUNICIPIO'].unique().tolist())
        seleccion = st.multiselect("Municipios:", municipios, default=[municipios[0]])
    
    df_filtrado = data[data['MUNICIPIO'].isin(seleccion)]

    # --- FILA 1: TENDENCIA (OCUPA TODO EL ANCHO) ---
    st.subheader("📈 Evolución Temporal de Energía Activa")
    fig_line = px.line(df_filtrado, x='YEAR', y='ENERGÍA ACTIVA', color='MUNICIPIO', 
                       markers=True, template="plotly_white", height=400)
    fig_line.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # --- FILA 2: DISPERSIÓN E HISTOGRAMA (DOS COLUMNAS) ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Dispersión: Potencia vs Energía")
        if 'POTENCIA MÁXIMA' in df_filtrado.columns:
            fig_scatter = px.scatter(df_filtrado, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', 
                                   color='MUNICIPIO', template="presentation", height=350)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Columna 'POTENCIA MÁXIMA' no disponible.")

    with col2:
        st.subheader("📊 Histograma de Frecuencias")
        fig_hist = px.histogram(df_filtrado, x='ENERGÍA ACTIVA', nbins=15, 
                               color_discrete_sequence=['#2E86C1'], template="simple_white", height=350)
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    # --- FILA 3: MATRIZ DE CORRELACIÓN (CENTREADA Y ESTILIZADA) ---
    st.subheader("🌡️ Matriz de Correlación de Variables")
    df_corr = df_filtrado.select_dtypes(include=['float64', 'int64']).corr()
    
    if not df_corr.empty:
        fig_corr = px.imshow(df_corr, text_auto=True, aspect="auto",
                            color_continuous_scale='RdBu_r', 
                            labels=dict(color="Correlación"))
        fig_corr.update_layout(height=400)
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # --- TABLA DE DATOS FINAL ---
    with st.expander("📝 Ver registros procesados"):
        st.dataframe(df_filtrado, use_container_width=True)

else:
    st.error("No se pudieron cargar los datos.")
