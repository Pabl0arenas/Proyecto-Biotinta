import streamlit as st
from PIL import Image #Cargar Imágenes 
logo=Image.open("UPB logo.png")   
st.set_page_config(page_title="Proyecto Biotintas", page_icon=logo,layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
h1 {
    padding-top: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# Crear columnas para alinear logo y título
col1, col2 = st.columns([0.1,0.9])

with col1:
    st.markdown("""
<style>
div.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)
    st.image(logo,width=100)
    
with col2:
     st.title("Proyecto Biotintas")
        
 #Actualizar fecha en el sidebar    

with st.sidebar:
    with st.container(border=True):
        st.markdown("📅 **Última actualización:** 12-03-2026")

#Creamos la sección de selección en el sidebar para ver diferentes resultados

secciones= ["Inicio","Parámetros de Impresión","Parámetros de Forma","Ensayos Reológicos","Ensayos Mecánicos","Ensayos Biológicos"]

Choice= st.sidebar.selectbox("Secciones", secciones)

# Llamamos las funciones de cada sección con sus datos

from forma import forma
from reologia import reo
from bio import bio

if Choice == "Inicio":
    st.markdown("""
    <div style="
        border: 2px solid #E0E0E0;
        border-radius: 12px;
        padding: 25px;
        background-color: #FAFAFA;
    ">
        <h3>🏠 Inicio</h3>
        <p>
        Bienvenido al <b>Dashboard del Proyecto Biotintas</b>.
        <br><br>
        Utiliza el panel lateral para explorar las seccionesdel proyecto.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
elif Choice == "Parámetros de Forma":
   st.header("🔬 Parámetros de Forma")
   forma()
if Choice == "Ensayos Reológicos":
   st.header("💧 Ensayos Reológicos")
   reo()
if Choice == "Ensayos Biológicos":
   st.header("🧫 Ensayos Biológicos")
   bio()
if Choice == "Parámetros de Impresión":
   from impresion import impresion
   st.header("🖨️ Parámetros de Impresión")
   impresion()
if Choice == "Ensayos Mecánicos":
   from mecanicas import mecanicas
   st.header("🛠️ Ensayos Mecánicos")
   mecanicas()
