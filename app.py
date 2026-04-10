import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard ZNI - Ingeniería", layout="wide")

# URL del archivo (Asegúrate de que el nombre coincida exactamente en GitHub)
URL = "https://raw.githubusercontent.com/Virolero24/ZNI-de-Colombia/refs/heads/main/datos_processed.csv"

@st.cache_data(ttl=5)
def load_and_clean():
    # Leemos el CSV
    df = pd.read_csv(URL)
    
    # 1. Limpieza de columnas
    df.columns = [str(c).strip().upper() for c in df.columns]
    if 'AÑO SERVICIO' in df.columns:
        df = df.rename(columns={'AÑO SERVICIO': 'AÑO'})
    
    # 2. LIMPIEZA MANUAL (Evita el error de 'arg must be a list')
    # En lugar de pd.to_numeric, usamos una función lambda que es más tolerante
    def forzar_numero(valor):
        try:
            return float(valor)
        except:
            return None

    df['AÑO SERVICIO'] = df['AÑO SERVICIO'].apply(forzar_numero)
    df['ENERGÍA ACTIVA'] = df['ENERGÍA ACTIVA'].apply(forzar_numero)
    df['POTENCIA MÁXIMA'] = df['POTENCIA MÁXIMA'].apply(forzar_numero)

    # 3. Limpieza de Municipios
    df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.upper().str.strip()
    replacements = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    for k, v in replacements.items():
        df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(k, v)

    # 4. Eliminar filas con errores de conversión
    df = df.dropna(subset=['AÑO SERVICIO', 'ENERGÍA ACTIVA'])
    
    # 5. Agrupación final
    df = df.groupby(['MUNICIPIO', 'AÑO SERVICIO'], as_index=False).agg({
        'ENERGÍA ACTIVA': 'sum',
        'POTENCIA MÁXIMA': 'max'
    })
    
    return df.sort_values(['MUNICIPIO', 'AÑO SERVICIO'])

try:
    df = load_and_clean()
    
    st.title("⚡ Transición Energética Justa - ZNI")
    
    # KPIs
    m1, m2, m3 = st.columns(3)
    m1.metric("Municipios", len(df['MUNICIPIO'].unique()))
    m2.metric("Impacto Estratégico", "70.18%")
    m3.metric("Año Máximo", int(df['AÑO SERVICIO'].max()) if not df.empty else 0)

    st.divider()

    # 1. Gráfico de Dispersión
    st.subheader("📊 Distribución de Demanda")
    lista_m = sorted(df['MUNICIPIO'].unique().tolist())
    sel_scatter = st.multiselect("Filtrar municipios:", lista_m, default=lista_m, key="s_final")
    
    if sel_scatter:
        df_s = df[df['MUNICIPIO'].isin(sel_scatter)]
        fig1 = px.scatter(df_s, x='POTENCIA MÁXIMA', y='ENERGÍA ACTIVA', color='MUNICIPIO', 
                         hover_name='MUNICIPIO', template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)

    # 2. Gráfico de Líneas
    st.divider()
    st.subheader("📈 Histórico y Proyección IA (2025-2028)")
    default_m = [m for m in ['SAN ANDRES'] if m in lista_m] or [lista_m[0]]
    sel_line = st.multiselect("Seleccionar para tendencia:", lista_m, default=default_m, key="l_final")
    
    if sel_line:
        df_l = df[df['MUNICIPIO'].isin(sel_line)]
        fig2 = px.line(df_l, x='AÑO SERVICIO', y='ENERGÍA ACTIVA', color='MUNICIPIO', markers=True)
        
        # Sombreado de predicción
        if df['AÑO SERVICIO'].max() >= 2025:
            fig2.add_vrect(x0=2024.5, x1=2028.5, fillcolor="rgba(46, 204, 113, 0.2)", 
                           layer="below", line_width=0, annotation_text="PREDICCIÓN IA")
        
        st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error("Error crítico en el Dashboard")
    st.write("Detalle del error:", e)

except Exception as e:
    st.error(f"Error detectado: {e}")
    st.info("Revisa que el archivo CSV tenga los datos de predicción correctamente.")
