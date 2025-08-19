import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🎲",
    layout='wide'
)

#image_path = "/Users/gnasa/Desktop/Projetos locais/Jupyter Notebook/"
image = Image.open('logo.jpeg')
st.sidebar.image (image, width=120)

st.sidebar.markdown("# GeoHub\n## Fastest Delivery in Town\n---")

st.write("# GeoHub Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard Foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
        - @gabrielnasatto

""")