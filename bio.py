import streamlit as st
import pandas as pd
import plotly.express as px

def bio():  
    st.info("📌 **Nota:** Se empleó reticulante TPP al 1 %")
    # === 1. Cargar data ===
    df = pd.read_excel("Viabilidad.xlsx", engine="openpyxl")

    fig = px.line(
    df,
    x="Tiempo",
    y="Viabilidad",
    color="Muestra",
    facet_col="Celula",
    markers=True,
    error_y="SD",
    category_orders={
        "Tiempo": [24, 48, 72]
    },
    labels={
        "Tiempo": "Tiempo (h)",
        "Viabilidad": "Viabilidad celular (%)",
        "Muestra": "Tipo de muestra",
        "Celula": "Tipo de célula"
    }
)
    st.subheader("Fibroblastos L929")
    st.markdown("**Viabilidad celular en función del tiempo**")
    fig.update_layout(
    template="simple_white",
    height=450,
    legend_title_text="Muestra",
    showlegend=True
)
   # Remover prefijo "Tipo de célula=" del título de los subplots
    for annotation in fig.layout.annotations:
        if annotation.text:
            annotation.text = annotation.text.replace("Tipo de célula=", "")

    fig.update_yaxes(
    range=[0, 110],
    ticksuffix=" %"
)
    fig.update_xaxes(
    tickmode="array",
    tickvals=[24, 48, 72]
)
    st.plotly_chart(fig, width='stretch')
    st.divider()
    #Imágenes
    st.subheader("Imágenes representativas")
    # Sección NCV
    st.markdown("### NCV")

    # Células sembradas (SEM)
    st.markdown("#### Células sembradas")
    cols = st.columns(3)
    sem_images_ncv = [
        ("NCV 24H SEM.png", "24 h"),
        ("NCV 48H SEM.png", "48 h"),
        ("NCV 72H SEM.png", "72 h"),
    ]
    for col, (fname, caption) in zip(cols, sem_images_ncv):
        with col:
            st.image(fname, use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-weight:bold;'>{caption}</p>", unsafe_allow_html=True)

    # Células embebidas (EMB)
    st.markdown("#### Células embebidas")
    cols = st.columns(3)
    emb_images_ncv = [
        ("NCV 24H EMB.png", "24 h"),
        ("NCV 48H EMB.png", "48 h"),
        ("NCV 72H EMB.png", "72 h"),
    ]
    for col, (fname, caption) in zip(cols, emb_images_ncv):
        with col:
            st.image(fname, use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-weight:bold;'>{caption}</p>", unsafe_allow_html=True)

    # Sección NCB
    st.markdown("### NCB")

    # Células sembradas (SEM)
    st.markdown("#### Células sembradas")
    cols = st.columns(3)
    sem_images_ncb = [
        ("NCB 24H SEM.png", "24 h"),
        ("NCB 48H SEM.png", "48 h"),
        ("NCB 72H SEM.png", "72 h"),
    ]
    for col, (fname, caption) in zip(cols, sem_images_ncb):
        with col:
            st.image(fname, use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-weight:bold;'>{caption}</p>", unsafe_allow_html=True)

    # Células embebidas (EMB)
    st.markdown("#### Células embebidas")
    cols = st.columns(3)
    emb_images_ncb = [
        ("NCB 24H EMB.png", "24 h"),
        ("NCB 48H EMB.png", "48 h"),
        ("NCB 72H EMB.png", "72 h"),
    ]
    for col, (fname, caption) in zip(cols, emb_images_ncb):
        with col:
            st.image(fname, use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-weight:bold;'>{caption}</p>", unsafe_allow_html=True)

    # Mostrar tabla
    with st.expander("Ver Tabla Resumen"):
        st.dataframe(df)

if __name__ == '__main__':
    bio()
