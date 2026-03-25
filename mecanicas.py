def mecanicas():
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    import numpy as np

    @st.cache_data
    def load_data():
        df = pd.read_excel("Mecánicos.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip()
        return df

    def _find_column(df: pd.DataFrame, candidates):
        cols_lower = {c.lower(): c for c in df.columns}
        for cand in candidates:
            cand_l = cand.lower()
            for col_l, col in cols_lower.items():
                if cand_l == col_l or cand_l in col_l or col_l in cand_l:
                    return col
        return None

    st.header("Gráficos de Medias")
    df = load_data()

    # Detectar columna de muestra
    sample_candidates = ["Muestra", "Tipo de muestra", "Tipo", "Sample", "Sample Type"]
    sample_col = _find_column(df, sample_candidates)
    if sample_col is None:
        sample_col = st.selectbox("Seleccione la columna que identifica la muestra", df.columns)

    muestras = sorted(df[sample_col].dropna().unique().tolist())
    muestra_seleccionada = st.sidebar.multiselect("Filtrar por Muestra", muestras, default=muestras)

    df_filtrado = df[df[sample_col].isin(muestra_seleccionada)].copy()

    # Detectar columnas de Módulo de Young y Tenacidad
    modulus_candidates = ["Módulo de Young", "Modulo de Young", "Young", "Young's Modulus", "E", "Modulo"]
    tenacity_candidates = ["Tenacidad", "tenacidad", "Toughness", "Tenacidad (J)", "Tenacidad (kJ/m2)"]

    mod_col = _find_column(df, modulus_candidates)
    ten_col = _find_column(df, tenacity_candidates)

    col_options = list(df.columns)
    if mod_col is None:
        mod_col = st.selectbox("Seleccione la columna para Módulo de Young", col_options, index=0)
    if ten_col is None:
        default_index = 1 if len(col_options) > 1 else 0
        ten_col = st.selectbox("Seleccione la columna para Tenacidad", col_options, index=default_index)

    # Asegurar valores numéricos
    df_filtrado[mod_col] = pd.to_numeric(df_filtrado[mod_col], errors='coerce')
    df_filtrado[ten_col] = pd.to_numeric(df_filtrado[ten_col], errors='coerce')

    # Calcular medias y desviaciones por muestra.
    # Si existen columnas SD1/SD2 en el fichero, úsalas como desviaciones para Modulo y Tenacidad respectivamente.
    sd1_candidates = ['SD1', 'Sd1', 'sd1']
    sd2_candidates = ['SD2', 'Sd2', 'sd2']
    sd1_col = _find_column(df_filtrado, sd1_candidates)
    sd2_col = _find_column(df_filtrado, sd2_candidates)

    if sd1_col and sd2_col:
        agg = df_filtrado.groupby(sample_col).agg({
            mod_col: 'mean',
            ten_col: 'mean',
            sd1_col: 'mean',
            sd2_col: 'mean'
        })
        agg = agg.rename(columns={
            mod_col: f"{mod_col}_mean",
            ten_col: f"{ten_col}_mean",
            sd1_col: f"{mod_col}_std",
            sd2_col: f"{ten_col}_std",
        }).reset_index()
    else:
        agg = df_filtrado.groupby(sample_col).agg({mod_col: ['mean', 'std'], ten_col: ['mean', 'std']})
        agg.columns = ['_'.join(col).strip() for col in agg.columns.values]
        agg = agg.reset_index()

    # Gráfico 1: Módulo de Young
    fig_mod = go.Figure()
    fig_mod.add_trace(go.Bar(
        x=agg[sample_col],
        y=agg[f"{mod_col}_mean"],
        name="Módulo de Young",
        error_y=dict(type='data', array=agg[f"{mod_col}_std"].fillna(0)),
    ))
    fig_mod.update_layout(xaxis_title="Muestra", yaxis_title=f"{mod_col}", title="Módulo de Young")

    # Gráfico 2: Tenacidad
    fig_ten = go.Figure()
    fig_ten.add_trace(go.Bar(
        x=agg[sample_col],
        y=agg[f"{ten_col}_mean"],
        name="Tenacidad",
        error_y=dict(type='data', array=agg[f"{ten_col}_std"].fillna(0)),
    ))
    fig_ten.update_layout(xaxis_title="Muestra", yaxis_title=f"{ten_col}", title="Tenacidad")

    st.plotly_chart(fig_mod, use_container_width="stretch")
    st.plotly_chart(fig_ten, use_container_width="stretch")

    # Mostrar tabla
    with st.expander("Ver Tabla Resumen"):
        st.dataframe(df)
    


if __name__ == '__main__':
    mecanicas()