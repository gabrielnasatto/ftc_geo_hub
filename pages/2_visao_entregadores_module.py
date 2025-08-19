# Libraries
from haversine import haversine
import numpy as np
import pandas as pd
import streamlit as st
import datetime
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

#---------------------------------------------------------------
#Funções
#---------------------------------------------------------------
def clean_code(df):
    """ Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Remoção dos valores NaN
        2. Conversão de tipos de dados específicos
        3. Strip dos dados
        4. Formatação de colunas de Datas
        5. Outros ajustes

        Input: Dataframe
        Output: Dataframe
    """
    # Substituir valores 'NaN ' por NaN real e remover linhas com NaN
    df = df.replace('NaN ', np.nan).dropna()
    
    # Conversões de tipo
    df['Delivery_person_Age'] = pd.to_numeric(df['Delivery_person_Age'])
    df['Delivery_person_Ratings'] = pd.to_numeric(df['Delivery_person_Ratings'])
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
    
    # Limpeza de strings (strip em todas as colunas de texto)
    str_cols = df.select_dtypes(include='object').columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
    
    # Ajustes específicos
    df['Weatherconditions'] = df['Weatherconditions'].str.replace('conditions', '', regex=False)
    df['Time_taken(min)'] = df['Time_taken(min)'].str.replace('(min)', '', regex=False).str.strip()
    df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')
    return df

def top_delivers(df, top_asc):
    # Calcular a média de 'Time_taken(min)' por cidade e entregador
    media_lenta = (df.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
                   .mean()
                   .reset_index()
                   .sort_values(by=['City', 'Time_taken(min)'], ascending=top_asc)
                   .groupby('City')
                   .head(10))
    media_lenta = media_lenta.reset_index(drop=True)  
    return media_lenta

# Import dataset
dados = pd.read_csv('dataset/train.csv')

#---------------------------------------------------------------
#Limpando os dados
df = clean_code(dados)

#============================================================
# Barra lateral
#============================================================
st.header('Marketplace - Visão Entregadores')

image_path = ('logo.jpeg')
image = Image.open( image_path )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# GeoHub')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022, 4, 13),
    min_value=datetime.datetime(2022, 2, 11),
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Power by Gabriel Nasatto')

#Filtros de Data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#Filtros de trânsito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#============================================================
#  Layout no Streamlit
#============================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1: 
            maior_idade = df['Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)

        with col2: 
            menor_idade = df['Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3: 
            melhor_condicao = df['Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)
            
        with col4: 
            pior_condicao = df['Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)
    
    with st.container():
        st.markdown("""___""")
        st.title('Avaliacoes')

        col1, col2 = st.columns (2)
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            avaliacao_media_entregador = (df[['Delivery_person_ID','Delivery_person_Ratings']]
                                          .groupby('Delivery_person_ID')
                                          .mean()
                                          .reset_index())
            st.dataframe(avaliacao_media_entregador)

        with col2:
            st.markdown('##### Avaliação média por Trânsito')
            avaliacao_media_transito = (df[['Road_traffic_density', 'Delivery_person_Ratings']]
                                        .groupby('Road_traffic_density')
                                        .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            avaliacao_media_transito.columns = ['delivery_mean', 'delivery_std']
            avaliacao_media_transito = avaliacao_media_transito.reset_index()
            st.dataframe(avaliacao_media_transito)
            
            st.markdown('##### Avaliação média por Clima')
            avaliacao_media_clima = (df[['Delivery_person_Ratings', 'Weatherconditions']]
                                     .groupby('Weatherconditions')
                                     .agg({'Delivery_person_Ratings':['mean', 'std']}))
            avaliacao_media_clima.columns = ['delivery_mean', 'delivery_std']
            avaliacao_media_clima = avaliacao_media_clima.reset_index()
            st.dataframe(avaliacao_media_clima)

        with st.container():
            st.markdown("___")
            st.title('Velocidade de Entrega')
        
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('##### Top 10 Entregadores Mais Rápidos por Cidade (Média)')
                media_rapida = top_delivers(df, top_asc=True)
                st.dataframe( media_rapida)
        
            with col2:
                st.markdown('##### Top 10 Entregadores Mais Lentos por Cidade (Média)')
                media_lenta = top_delivers(df, top_asc=False)
                st.dataframe( media_lenta)

















        




























        