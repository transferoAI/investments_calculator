import yfinance as yf
import pandas as pd
from datetime import date, datetime, timedelta

def obter_dados_yfinance(simbolo, data_fim):
    """
    Obtém dados de um ativo do Yahoo Finance.
    
    Args:
        simbolo (str): Símbolo do ativo no Yahoo Finance
        data_fim (date): Data final para obtenção dos dados
    
    Returns:
        pd.DataFrame: DataFrame com os dados do ativo
    """
    # Calculando a data inicial (5 anos atrás)
    data_inicio = data_fim - timedelta(days=5*365)
    
    try:
        # Obtendo os dados do Yahoo Finance
        ticker = yf.Ticker(simbolo)
        dados = ticker.history(
            start=data_inicio,
            end=data_fim,
            interval='1mo'
        )
        
        # Calculando o retorno mensal
        dados['retorno'] = dados['Close'].pct_change() * 100
        
        # Removendo a primeira linha (NaN)
        dados = dados.dropna()
        
        # Adicionando a coluna de índice para referência
        dados['index'] = dados.index
        
        return dados
        
    except Exception as e:
        print(f"Erro ao obter dados do Yahoo Finance: {e}")
        return None

# Símbolos dos ativos para referência:
# IBOVESPA: ^BVSP
# S&P 500: ^GSPC
# Dólar (USD/BRL): BRL=X
# Ouro: GC=F 