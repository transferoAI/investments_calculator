import pandas as pd
import requests
import streamlit as st

def obter_serie_bcb(codigo_serie, data_inicio, data_fim):
    """
    Obtém dados de uma série do Banco Central do Brasil.
    
    Args:
        codigo_serie (int): Código da série no BCB
        data_inicio (str): Data inicial no formato dd/mm/yyyy
        data_fim (str): Data final no formato dd/mm/yyyy
        
    Returns:
        pd.DataFrame: DataFrame com os dados da série
    """
    try:
        url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}'
        response = requests.get(url)
        response.raise_for_status()
        dados = response.json()
        df = pd.DataFrame(dados)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].astype(float)
        df['ano_mes'] = df['data'].dt.to_period('M')
        return df.groupby('ano_mes')['valor'].mean().reset_index()
    except Exception as e:
        st.warning(f"Erro ao obter dados da série {codigo_serie} do BCB: {e}")
        return pd.DataFrame(columns=['ano_mes', 'valor']) 