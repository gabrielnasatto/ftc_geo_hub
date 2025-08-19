# ============================================================
# Libraries
# ============================================================
import datetime
import numpy as np
import pandas as pd
import streamlit as st
from haversine import haversine
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Visão Restaurante', page_icon='🍽️', layout='wide')

# ============================================================
# Funções de Limpeza
# ============================================================
def clean_code(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpeza do dataframe:
      1. Remove valores NaN
      2. Converte tipos de dados
      3. Strip em strings
      4. Ajusta colunas específicas
    """
    df = df.replace("NaN ", np.nan).dropna()

    # Conversões
    df["Delivery_person_Age"] = pd.to_numeric(df["Delivery_person_Age"])
    df["Delivery_person_Ratings"] = pd.to_numeric(df["Delivery_person_Ratings"])
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%d-%m-%Y")

    # Strip em todas as colunas de texto
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].str.strip()

    # Ajustes específicos
    df["Weatherconditions"] = df["Weatherconditions"].str.replace("conditions", "", regex=False)
    df["Time_taken(min)"] = (
        df["Time_taken(min)"]
        .str.replace("(min)", "", regex=False)
        .str.strip()
        .astype(float)
    )

    return df


# ============================================================
# Funções de Métricas e Gráficos
# ============================================================
def distance(df: pd.DataFrame, return_fig: bool = False):
    """Calcula a distância média ou retorna gráfico de pizza por cidade"""
    cols = [
        "Delivery_location_latitude", "Delivery_location_longitude",
        "Restaurant_latitude", "Restaurant_longitude"
    ]

    df["Distance"] = df[cols].apply(
        lambda x: haversine(
            (x["Delivery_location_latitude"], x["Delivery_location_longitude"]),
            (x["Restaurant_latitude"], x["Restaurant_longitude"])
        ),
        axis=1,
    )

    if not return_fig:
        return np.round(df["Distance"].mean(), 2)

    df_aux = df.groupby("City", as_index=False)["Distance"].mean()
    return go.Figure(
        data=[go.Pie(labels=df_aux["City"], values=df_aux["Distance"], pull=[0, 0.1, 0])]
    )


def avg_std_time_delivery(df: pd.DataFrame, festival: str, op: str) -> float:
    """Retorna tempo médio ou desvio padrão de entregas em festivais"""
    df_aux = (
        df.groupby("Festival")["Time_taken(min)"]
        .agg(["mean", "std"])
        .rename(columns={"mean": "avg_time", "std": "std_time"})
        .reset_index()
    )

    value = df_aux.loc[df_aux["Festival"] == festival, op].values
    return np.round(value[0], 2) if len(value) else np.nan


def avg_std_time_on_traffic(df: pd.DataFrame):
    """Retorna gráfico Sunburst do tempo médio e std por cidade e trânsito"""
    df_aux = (
        df.groupby(["City", "Road_traffic_density"])["Time_taken(min)"]
        .agg(["mean", "std"])
        .rename(columns={"mean": "avg_time", "std": "std_time"})
        .reset_index()
    )

    return px.sunburst(
        df_aux,
        path=["City", "Road_traffic_density"],
        values="avg_time",
        color="std_time",
        color_continuous_scale="RdBu",
        color_continuous_midpoint=np.average(df_aux["std_time"]),
    )


# ============================================================
# Import e Limpeza
# ============================================================
df = pd.read_csv("dataset/train.csv")
df = clean_code(df)


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


# ============================================================
# Layout no Streamlit
# ============================================================
tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "_", "_"])

with tab1:
    # ---------------------------
    # Métricas principais
    # ---------------------------
    st.markdown("___")
    st.title("Overall Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Entregadores Únicos", df["Delivery_person_ID"].nunique())
    col2.metric("Distância Média das Entregas", distance(df, return_fig=False))
    col3.metric("Tempo Médio (Festival)", avg_std_time_delivery(df, "Yes", "avg_time"))
    col4.metric("Desvio Padrão (Festival)", avg_std_time_delivery(df, "Yes", "std_time"))
    col5.metric("Tempo Médio (Sem Festival)", avg_std_time_delivery(df, "No", "avg_time"))
    col6.metric("Desvio Padrão (Sem Festival)", avg_std_time_delivery(df, "No", "std_time"))

    # ---------------------------
    # Tempo médio por cidade
    # ---------------------------
    st.markdown("___")
    st.title("Tempo Médio de Entrega por Cidade")

    df_aux = (
        df.groupby("City")["Time_taken(min)"]
        .agg(["mean", "std"])
        .rename(columns={"mean": "avg_time", "std": "std_time"})
        .reset_index()
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Control",
            x=df_aux["City"],
            y=df_aux["avg_time"],
            error_y=dict(type="data", array=df_aux["std_time"]),
        )
    )
    st.plotly_chart(fig)

    # ---------------------------
    # Distribuição do Tempo
    # ---------------------------
    st.markdown("___")
    st.title("Distribuição do Tempo")
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(distance(df, return_fig=True))
    with col2:
        st.plotly_chart(avg_std_time_on_traffic(df))

    # ---------------------------
    # Distribuição da Distância
    # ---------------------------
    st.markdown("___")
    cols = ["City", "Time_taken(min)", "Type_of_order"]
    df_aux = (
        df.groupby(["City", "Type_of_order"])["Time_taken(min)"]
        .agg(["mean", "std"])
        .rename(columns={"mean": "avg_time", "std": "std_time"})
        .reset_index()
    )
    st.dataframe(df_aux)
