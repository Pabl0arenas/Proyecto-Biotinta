import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# cache only the data-loading logic, not the entire UI
@st.cache_data

def load_data():
    # lee el Excel y devuelve el DataFrame
    return pd.read_excel("Consolidado resultados.xlsx", engine="openpyxl")


def forma():
    st.info("📌 **Nota:** Se empleó NCV o NCB al 1 %")

    st.markdown("---")
    with st.expander("ℹ️ Información sobre las Variables"):
        st.write("""
        - **Pr**:  índice de impribilidad. Pr < 1: Poros  demasiado circulares. Pr= 1: Poros cuadrados. Pr >1: Poros irregulares.
        - **Conformación**: Nivel de fidelidad entre la plantilla y el constructo.
        - **Colapso de Filamento (°)**: Ángulo de deflexión del filamento entre dos puntos de soporte.
    
        """)
    
    st.markdown("---")    
    # === 1. Cargar data ===
    df = load_data()

    # Asegurar tipo fecha
    #df["Fecha"] = pd.to_datetime(df["Fecha"])

    # === 2. Filtro multiselect de biotintas ===
    biotintas = df["Biotinta"].unique()

    filtro_biotintas = st.sidebar.multiselect(
        "Seleccionar Biotinta(s)",options=biotintas, default=biotintas)  # Por defecto todas visibles

    # Aplicar filtro
    df_filtrado = df[df["Biotinta"].isin(filtro_biotintas)]
    
    # ======================================================
    # === 3. GRAFICO 1: Pr vs Fecha ========================
    # ======================================================


    fig_pr = px.line(df_filtrado, x="Fecha", y="Pr", color="Biotinta", markers=True, title="Pr vs Fecha ")
    fig_pr.add_hline(y=1, line_color="red", line_dash="dash")
    st.plotly_chart(fig_pr, width='stretch')
    st.divider()
    # ======================================================
    # === 4. GRAFICO 2: Conformación vs Fecha ==============
    # ======================================================
    fig_conf = px.line(
        df_filtrado,
        x="Fecha",
        y="Conformación",
        color="Biotinta",
        markers=True,
        title="Conformación vs Fecha"
    )
    st.plotly_chart(fig_conf, width='stretch')
    st.divider()
    # ======================================================
    # === 5. GRAFICO 3: Colapso de filamento vs Fecha ======
    # ======================================================


    fig_colapso = px.line(
        df_filtrado,
        x="Fecha",
        y="Colapso del filamento (°)",
        color="Biotinta",
        markers=True,
        title="Colapso del filamento (°) vs Fecha"
    )
    st.plotly_chart(fig_colapso, width='stretch')
    st.divider()

    
    st.divider()
    # === Gráficos de medias con desviación estándar ===
    st.subheader("📊 Medias ± Desviación Estándar por Biotinta")
    
    stats_cols = ["Pr", "Conformación", "Colapso del filamento (°)"]
    display_names = {
        "Pr": "Pr",
        "Conformación": "Conformación",
        "Colapso del filamento (°)": "Colapso del filamento (°)"
    }

    # Calcular media y desviación estándar por Biotinta
    stats = df_filtrado.groupby("Biotinta")[stats_cols].agg(["mean", "std"])
    stats.columns = [f"{var}_{stat}" for var, stat in stats.columns]
    stats = stats.reset_index()

    # Crear un gráfico para cada variable
    for var in stats_cols:
        mean_col = f"{var}_mean"
        std_col = f"{var}_std"
        if mean_col not in stats.columns or std_col not in stats.columns:
            continue
        df_v = stats[["Biotinta", mean_col, std_col]].rename(
            columns={mean_col: "mean", std_col: "std"}
        )
        title = f"Media ± desviación estándar de {display_names.get(var, var)} por Biotinta"
        fig_stats = px.bar(
            df_v,
            x="Biotinta",
            y="mean",
            error_y="std",
            labels={
                "mean": "Media",
                "std": "Desviación estándar",
                "Biotinta": "Biotinta",
            },
            title=title,
        )
        fig_stats.update_layout(template="plotly_white")
        st.plotly_chart(fig_stats, use_container_width=True)

        # === Matriz de correlación entre variables ===
    st.subheader("🔗 Correlación entre Variables")
    
    variables_corr = ["Pr", "Conformación", "Colapso del filamento (°)"]
    df_variables = df_filtrado[variables_corr].copy()
    correlacion = df_variables.corr()
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=correlacion.values,
        x=variables_corr,
        y=variables_corr,
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


    # === Gráfico Radial Normalizado ===
    st.subheader("🕸 Comparación Radial (Min-Max Scaling)")
    
    variables = ["Pr", "Conformación", "Colapso del filamento (°)"]
    radar_labels = [var.split('(')[0].strip() for var in variables]
    
    # Promedio por Biotinta
    df_avg = df_filtrado.groupby("Biotinta")[variables].mean().reset_index()
    
    # === Min-Max Scaling ===
    df_norm = df_avg.copy()
    
    for col in variables:
        min_val = df_norm[col].min()
        max_val = df_norm[col].max()
        
        if max_val - min_val != 0:
            df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
        else:
            df_norm[col] = 0
    
    # Crear figura radar
    fig_radar = go.Figure()
    
    for i in range(len(df_norm)):
        fig_radar.add_trace(go.Scatterpolar(
            r=df_norm.loc[i, variables].values,
            theta=radar_labels,
            fill='toself',
            name=df_norm.loc[i, "Biotinta"]
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="Gráfico Radial Normalizado"
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()
    # Mostrar tabla
    with st.expander("Ver Tabla Resumen"):
        st.dataframe(df_filtrado)

if __name__ == '__main__':
    forma()



