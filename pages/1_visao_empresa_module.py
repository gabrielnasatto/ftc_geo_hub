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
import plotly.graph_objects as go

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

#---------------------------------------------------------------
#Funções
#---------------------------------------------------------------
def country_maps(df):
    df_aux = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    map = folium.Map()  
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude' ],
                        location_info['Delivery_location_longitude' ] ],
                        popup=location_info[['City', 'Road_traffic_density' ]] ) . add_to(map)
    folium_static(map, width= 1024, height=600)

def order_share_by_week(df):
    # Quantidade de pedidos / Número único de entregadores por semana
    df_aux1 = df.loc[:,['ID', 'Week_of_Year']].groupby('Week_of_Year').count().reset_index()
    df_aux2 = df.loc[:, ['Delivery_person_ID', 'Week_of_Year']].groupby('Week_of_Year').nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    df_aux['Order_by_Delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='Week_of_Year', y='Order_by_Delivery')
    return fig

def order_by_week(df):
    #criar a coluna de semana
    df['Week_of_Year'] = df['Order_Date'].dt.strftime('%U')
    df_aux = df.loc[:, ['ID', 'Week_of_Year']].groupby('Week_of_Year').count().reset_index()
    fig = px.line(df_aux, x='Week_of_Year', y='ID')
    return df

def traffic_order_city(df):
    df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID')
    return fig

def traffic_order_share(df):
    df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux['Entregas %'] = df_aux['ID'] / (df_aux['ID'].sum())
    fig = px.pie(df_aux, values='Entregas %', names='Road_traffic_density')
    return fig

def order_metric(df):
    #Contagem de colunas ID agrupando Order Date e usar a biblioteca de visualização de dados pra criar o gráfico
    #colunas
    cols = ['ID', 'Order_Date']
    
    #selecao das linhas
    df_aux = df.loc[:, cols].groupby('Order_Date').count().reset_index()

    #desenhar o gráfico
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig
    
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

#---------------Início da estrutura lógica do código -----------
#---------------------------------------------------------------
# Import dataset
dados = pd.read_csv('dataset/train.csv')

#---------------------------------------------------------------
#Limpando os dados
df = clean_code(dados)

#============================================================
# Barra lateral
#============================================================
st.header('Marketplace - Visão Clientes')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        st.markdown('# Orders by Day')
        fig = order_metric(df)
        st.plotly_chart( fig, use_container_width = True, key="grafico_order_metric")
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header("Traffic Order Share")
            fig = traffic_order_share(df)
            st.plotly_chart(fig, use_container_width=True, key="grafico_traffic_order_share")

        with col2:
            st.header("Traffic Order City")
            fig = traffic_order_city(df)
            st.plotly_chart(fig, use_container_width=True,key="grafico_traffic_order_city")
with tab2:
    with st.container():
        st.markdown("# Order by Week")
        st.plotly_chart(fig, use_container_width=True,key="grafico_order_by_week")
        fig = order_by_week(df)
        
    with st.container():
        st.markdown("# Order Share by Week")
        fig = order_share_by_week(df)
        st.plotly_chart(fig, use_container_width=True,key="grafico_order_share_by_week")
        
with tab3:
    st.markdown("# Country Maps")
    country_maps(df)

    












