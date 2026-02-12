import streamlit as st
import pandas as pd
import plotly.express as px


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

            st.plotly_chart(fig, width="Stretch")
        else:
            st.warning(f"No se encontró la columna '{col_name}'")


if __name__ == "__main__":
    impresion()
