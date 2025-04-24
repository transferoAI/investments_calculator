import requests
import pandas as pd
from datetime import date, datetime, timedelta
import streamlit as st

def obter_dados_bcb(codigo, data_fim):
    """
    Obtém dados de um indicador do Banco Central do Brasil.
    
    Args:
        codigo (int): Código do indicador no BCB
        data_fim (date): Data final para obtenção dos dados
    
    Returns:
        pd.DataFrame: DataFrame com os dados do indicador
    """
    # Calculando a data inicial (5 anos atrás)
    data_inicio = data_fim - timedelta(days=5*365)
    
    # Formatando as datas para o formato do BCB
    data_inicio_str = data_inicio.strftime('%d/%m/%Y')
    data_fim_str = data_fim.strftime('%d/%m/%Y')
    
    # Construindo a URL da API
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados'
    params = {
        'formato': 'json',
        'dataInicial': data_inicio_str,
        'dataFinal': data_fim_str
    }
    
    try:
        # Fazendo a requisição
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Convertendo os dados para DataFrame
        dados = pd.DataFrame(response.json())
        
        # Convertendo a coluna de data
        dados['data'] = pd.to_datetime(dados['data'], format='%d/%m/%Y')
        dados.set_index('data', inplace=True)
        
        # Renomeando a coluna de valor
        dados.rename(columns={'valor': 'valor'}, inplace=True)
        
        # Adicionando a coluna de índice para referência
        dados['index'] = dados.index
        
        return dados
        
    except Exception as e:
        st.warning(f"Erro ao obter dados do BCB: {e}")
        return None

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