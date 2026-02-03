import streamlit as st
import pandas as pd
import plotly.express as px

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
    df = pd.read_excel("Consolidado resultados.xlsx", engine="openpyxl")

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
    # Mostrar tabla
    with st.expander("Ver Tabla Resumen"):
        st.dataframe(df_filtrado)

if __name__ == '__main__':
    forma()



