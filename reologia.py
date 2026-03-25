import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


# === 1. Cargar data ===
@st.cache_data
def load_data():
    df = pd.read_excel("reo2.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip()
    return df


def reo():
    # === 11. Información Variables ===
    st.markdown("---")
    with st.expander("ℹ️ Información sobre las Variables"):
        st.write("""
        - **Yield Stress (Pa)**:  Esfuerzo cortante mínimo que un material  debe superar para empezar a fluir 
        - **Cross Point (%)**: Punto que establece la transición del comportamiento similar a un sólido al comportamiento similar a un líquido del material
        - **Recovery (%)**: Capacidad del material para recuperar su forma original
        - **Average Filamente Diameter (cm)**: Medida del espesor promedio de los filamentos
        - **Expansion Ratio (cm)**: Cambio de tamaño del radio de los filamentos
        
        Cada variable incluye su **Desviación Estándar (SD)** para medir la variabilidad de los resultados.
        """)
    df = load_data()

    # Filtrar por muestra
    muestras = df['Muestra'].dropna().unique().tolist()
    muestra_seleccionada = st.sidebar.multiselect(
        "Seleccionar Biontinta(s):",
        muestras,
        default=muestras
    )

    # Filtrar dataframe
    df_filtrado = df[df['Muestra'].isin(muestra_seleccionada)]

    # Definir variables y sus desviaciones
    variables_config = {
        'Yield Stress (Pa)': {'desv': 'SD1'},
        'Cross Point (%)': {'desv': 'SD2'},
        'Recovery (%)': {'desv': 'SD3'},
        'Average Filamente Diameter (cm)': {'desv': 'SD4'},
        'Expansion Ratio (cm)': {'desv': 'SD5'}
    }

    variables_disponibles = list(variables_config.keys())

    # === 3. Resumen estadístico superior ===
    st.markdown("---")
    st.subheader("📈 Resumen Estadístico General")

    cols = st.columns(len(variables_disponibles))

    for idx, var in enumerate(variables_disponibles):
        if var in df_filtrado.columns:
            valor_promedio = df_filtrado[var].mean()
            desv_promedio = df_filtrado[variables_config[var]['desv']].mean()
            
            with cols[idx]:
                st.metric(
                    label=var,
                    value=f"{valor_promedio:.2f}",
                    delta=f"±{desv_promedio:.3f}",
                    delta_color="off"
                )

    # === 4. Gráfico de medias de variables ===
    st.markdown("---")
    st.subheader("📉 Medias de Variables")

    variable_linea = st.selectbox(
        "Selecciona variable para gráfico de medias:",
        variables_disponibles
    )

    # Crear gráfico de líneas con barras de error
    fig_linea = go.Figure()

    desv_col = variables_config[variable_linea]['desv']

    fig_linea.add_trace(go.Scatter(
        x=df_filtrado['Muestra'],
        y=df_filtrado[variable_linea],
        error_y=dict(
            type='data',
            array=df_filtrado[desv_col],
            visible=True
        ),
        mode='markers',
        hovertemplate="<b>%{x}</b><br>Valor: %{y:.2f}<br>Desviación: ±%{error_y.array:.3f}<extra></extra>"
    ))

    fig_linea.update_layout(
        title=variable_linea,
        xaxis_title="Muestra",
        yaxis_title=variable_linea,
        hovermode='x unified',
        template='plotly_white',
        height=500
    )

    st.plotly_chart(fig_linea, width="stretch")


    # === 6. Matriz de correlación entre variables ===
    st.markdown("---")
    st.subheader("🔗 Correlación entre Variables")

    df_variables = df_filtrado[variables_disponibles].copy()
    correlacion = df_variables.corr()

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=correlacion.values,
        x=variables_disponibles,
        y=variables_disponibles,
        colorscale='RdBu',
        zmid=0,
        text=np.round(correlacion.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlación")
    ))

    fig_heatmap.update_layout(
        title="Matriz de Correlación entre Variables",
        height=500
    )

    st.plotly_chart(fig_heatmap, width="stretch")

   

    # === 8. Gráfico Radial Normalizado ===
    st.markdown("---")
    st.subheader("🕸 Comparación Radial Normalizada (Min-Max Scaling)")
    
    # Calcular promedios por Muestra
    df_avg = df_filtrado.groupby("Muestra")[variables_disponibles].mean().reset_index()
    
    # Normalizar con Min-Max Scaling
    df_norm = df_avg.copy()
    
    for col in variables_disponibles:
        min_val = df_norm[col].min()
        max_val = df_norm[col].max()
        
        if max_val - min_val != 0:
            df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
        else:
            df_norm[col] = 0
    
    # Crear etiquetas sin unidades
    radar_labels = [var.split('(')[0].strip() for var in variables_disponibles]
    
    # Crear figura radar
    fig_radar = go.Figure()
    
    for i in range(len(df_norm)):
        fig_radar.add_trace(go.Scatterpolar(
            r=df_norm.loc[i, variables_disponibles].values,
            theta=radar_labels,
            fill='toself',
            name=df_norm.loc[i, "Muestra"]
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="Gráfico Radial Normalizado",
        height=600
    )
    
    st.plotly_chart(fig_radar, use_container_width="stretch")

    # === 9. Tabla de datos detallada ===
    


    with st.expander("Ver Tabla Resumen"):
        st.dataframe(
            df_filtrado,
            width="stretch",
            height=400
    )
    st.markdown("---")
    st.subheader("📚 Modelo Reológico de Carreau-Yasuda")

    with st.expander("📋 Información del Modelo", expanded=False):
        st.markdown("""
        ### Ecuación del Modelo:
        $$\\frac{\\eta - \\eta_\\infty}{\\eta_0 - \\eta_\\infty} = \\left[1 + (k\\dot{\\gamma})^a\\right]^{\\frac{n-1}{a}}$$
        
        ### Parámetros:
        - **η (eta)**: Viscosidad aparente a una tasa de corte considerada
        - **η₀ (eta cero)**: Viscosidad a una tasa de corte cero (meseta Newtoniana inferior)
        - **η∞ (eta infinito)**: Viscosidad a una tasa de corte infinita (meseta Newtoniana superior)
        - **k**: Tiempo característico o índice de consistencia [s]
        - **γ̇**: Tasa de corte [s⁻¹]
        - **n**: Índice de la ley de potencia (0 < n ≤ 1)
        - **a**: Parámetro de transición (controla la suavidad entre regiones)
        
        ### Comportamiento:
        Este modelo captura la transición de un fluido desde un comportamiento **Newtoniano a bajas velocidades 
        de cizalla** (donde η ≈ η₀) hacia un comportamiento de **ley de potencias a altas velocidades** (donde n < 1 
        indica comportamiento pseudoplástico o adelgazante por cizalla).
        """)
    
    st.divider()

    # === 0. Modelo de Carreau-Yasuda ===
    df2 = pd.read_excel("Ajustes curvas.xlsx", engine="openpyxl")
    
    # === 2. Filtro por Muestra ===
    df2["Fecha"] = pd.to_datetime(df2["Fecha"]).dt.date
    muestras_unicas = sorted(df2["Muestra"].unique())
    muestras_seleccionadas = st.multiselect("Seleccionar Biotinta(s)", muestras_unicas, default=muestras_unicas)
    df2_filtrado = df2[df2["Muestra"].isin(muestras_seleccionadas)]
    
    # === 3. Gráfico 1: Fecha vs ncero ===

    fig1 = px.scatter(df2_filtrado, x="Fecha", y="ncero", 
                      color="Muestra",
                      title="η₀ vs Fecha",
                      labels={"ncero": "η₀ (Pa·s)", "Fecha": "Fecha"})
    fig1.update_traces(mode='lines+markers')
    st.plotly_chart(fig1, width="stretch")
    
    st.divider()
    # === 4. Gráfico 2: Fecha vs ninf ===
    fig2 = px.scatter(df2_filtrado, x="Fecha", y="ninf",
                      color="Muestra",
                      title="η∞ vs Fecha",
                      labels={"ninf": "η∞ (Pa·s)", "Fecha": "Fecha"})
    fig2.update_traces(mode='lines+markers')
    st.plotly_chart(fig2, width="stretch")
    with st.expander("Otras variables del modelo"):
        st.dataframe(
            df2_filtrado,
            width="stretch",
            height=400)


if __name__ == '__main__':
    reo()
