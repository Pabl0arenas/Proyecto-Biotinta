import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


# === 1. Cargar data ===
@st.cache_data
def load_data():
    df = pd.read_excel("Parámetros de impresión.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip()
    return df


def impresion():
    df = load_data()

    # === Título y nota ===

    st.info("📌 **Nota:** Se empleó NCV o NCB al 1 %")
    st.markdown("---")
    with st.expander("ℹ️ Información sobre las Variables"):
        st.write("""
        - **Punta (G)**: Punta empleada para el proceso de impresión.
        - **Presión (kPa)**: Presión de trabajo.
        - **Velocidad (mm/s)**: Velocidad de la punta durante el proceso de impresión.
    
        """)
    st.markdown("---")



    # === Sidebar: filtro de Biotinta ===
    biotintas = df["Biotinta"].dropna().unique()

    filtro_biotintas = st.sidebar.multiselect(
        "Seleccionar Biotinta(s)",
        options=biotintas,
        default=biotintas
    )

    # Aplicar filtro por Biotinta
    df_filtrado = df[df["Biotinta"].isin(filtro_biotintas)].copy()

    # === Selectbox de Geometría (FUERA del sidebar) ===
    geometria_options = df_filtrado["Geometría"].dropna().unique().tolist()

    if not geometria_options:
        st.warning(
            "No hay valores en la columna 'Geometría' para las biotintas seleccionadas."
        )
        return

    seleccion_geometria = st.selectbox(
        "Seleccionar Geometría",
        options=geometria_options
    )

    # Filtrar por Geometría
    df_filtrado = df_filtrado[
        df_filtrado["Geometría"] == seleccion_geometria
    ].copy()

    # === Procesar Fecha ===
    if "Fecha" in df_filtrado.columns:
        df_filtrado["Fecha"] = pd.to_datetime(
            df_filtrado["Fecha"], errors="coerce"
        )
        df_filtrado = df_filtrado.sort_values("Fecha")
    else:
        st.warning("No se encontró la columna 'Fecha' en los datos.")
        return

    # === Gráficas (FACETAS POR BIOTINTA) ===
    plot_cols = [
        ("Punta (G)", "Punta (G)"),
        ("Presión (kPa)", "Presión (kPa)"),
        ("Velocidad (mm/s)", "Velocidad (mm/s)"),
    ]

    for col_name, display_name in plot_cols:
        if col_name in df_filtrado.columns:
            fig = px.line(
                df_filtrado,
                x="Fecha",
                y=col_name,
                facet_col="Biotinta",
                facet_col_wrap=2,      # ajusta si tienes muchas biotintas
                markers=True,
                labels={
                    col_name: display_name,
                    "Fecha": "Fecha"
                },
                title=f"{display_name} vs Fecha"
            )
            # Quitar "Biotinta=" de las facetas
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            # Ajustes clave para comparación correcta
            fig.update_layout(
                template="plotly_white",
                xaxis_title="Fecha",
                yaxis_title=display_name
            )

            # Todas las facetas comparten el mismo eje Y
            fig.update_yaxes(matches="y")

            st.plotly_chart(fig, width="stretch")
        else:
            st.warning(f"No se encontró la columna '{col_name}'")

    # === Gráficos de medias con desviación estándar ===
    # Se genera un gráfico independiente para cada variable (Punta, Presión, Velocidad)
    st.markdown("---")
    st.subheader("📊 Gráfico de medias")
    
    stats_cols = [col for col, _ in plot_cols if col in df_filtrado.columns]
    if stats_cols:
        # agrupamos por Biotinta
        stats = df_filtrado.groupby("Biotinta")[stats_cols].agg(["mean", "std"])
        stats.columns = [f"{var}_{stat}" for var, stat in stats.columns]
        stats = stats.reset_index()

        # mapear nombres de display si los tenemos
        display_map = {col: disp for col, disp in plot_cols}

        for var in stats_cols:
            mean_col = f"{var}_mean"
            std_col = f"{var}_std"
            if mean_col not in stats.columns or std_col not in stats.columns:
                continue
            df_v = stats[["Biotinta", mean_col, std_col]].rename(
                columns={mean_col: "mean", std_col: "std"}
            )
            title = f"{display_map.get(var, var)}"
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
    else:
        st.warning("No hay columnas válidas para calcular medias y desviaciones estándar.")
   
# === Matriz de correlación entre variables ===
    st.markdown("---")
    st.subheader("🔗 Correlación entre Variables")
    
    variables_corr = ["Punta (G)", "Presión (kPa)", "Velocidad (mm/s)"]
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
    # === Gráfico Radial Normalizado
    # =========================
    st.markdown("---")
    st.subheader("🕸 Comparación Radial (Min-Max Scaling)")

    variables = ["Punta (G)", "Presión (kPa)", "Velocidad (mm/s)"]
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

    st.plotly_chart(fig_radar, width="stretch")
if __name__ == "__main__":
    impresion()
