import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

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
    st.title("📊 Reporte Técnico ZNI")
    
    # Filtro en la barra lateral
    with st.sidebar:
        municipios = sorted(data['MUNICIPIO'].unique().tolist())
        seleccion = st.multiselect("Municipios:", municipios, default=[municipios[0]])
    
    df_filtrado = data[data['MUNICIPIO'].isin(seleccion)]

    # --- HISTOGRAMA ESTILO COLAB ---
    st.subheader("📊 Distribución de Energía Activa")
    
    # Creamos la figura con Matplotlib para que sea idéntica a Colab
    fig_hist, ax_hist = plt.subplots(figsize=(10, 4))
    sns.histplot(df_filtrado['ENERGÍA ACTIVA'], bins=20, kde=True, color='#2E86C1', ax=ax_hist)
    ax_hist.set_title('Distribución de Frecuencias (Energía Activa)', fontsize=12)
    ax_hist.set_xlabel('Energía (kWh)')
    ax_hist.set_ylabel('Frecuencia')
    ax_hist.grid(axis='y', alpha=0.3)
    
    # Lo mostramos en Streamlit usando pyplot
    st.pyplot(fig_hist)

    st.divider()

    # --- MATRIZ DE CORRELACIÓN ESTILO COLAB ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🌡️ Matriz de Correlación")
        df_corr = df_filtrado.select_dtypes(include=['float64', 'int64']).corr()
        
        fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
        sns.heatmap(df_corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax_corr, square=True)
        ax_corr.set_title('Correlación de Pearson')
        st.pyplot(fig_corr)

    with col2:
        st.subheader("📝 Resumen Estadístico")
        # Esto le da un toque muy pro de ingeniería
        st.dataframe(df_filtrado[['ENERGÍA ACTIVA', 'POTENCIA MÁXIMA']].describe())

    # --- GRÁFICO DE LÍNEAS (Mantenemos Plotly por la interactividad del tiempo) ---
    st.divider()
    st.subheader("📈 Tendencia Temporal")
    import plotly.express as px
    fig_line = px.line(df_filtrado, x='YEAR', y='ENERGÍA ACTIVA', color='MUNICIPIO', 
                       markers=True, template="simple_white")
    st.plotly_chart(fig_line, use_container_width=True)

else:
    st.error("No se pudieron cargar los datos.")
