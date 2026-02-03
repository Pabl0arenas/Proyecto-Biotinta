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
    
    fig.update_layout(
    title="Viabilidad celular en función del tiempo",
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
    # Mostrar tabla
    with st.expander("Ver Tabla Resumen"):
        st.dataframe(df)

if __name__ == '__main__':
    bio()
