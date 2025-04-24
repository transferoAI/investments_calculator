import yfinance as yf
import pandas as pd
from datetime import datetime

def obter_ibovespa_yfinance(data_inicio, data_fim):
    """
    Obtém dados do IBOVESPA via YFinance.
    
    Args:
        data_inicio (str): Data inicial no formato DD/MM/YYYY
        data_fim (str): Data final no formato DD/MM/YYYY
        
    Returns:
        pandas.DataFrame: DataFrame com os dados do IBOVESPA contendo as colunas:
            - ano_mes: Mês no formato YYYY-MM
            - valor: Variação percentual mensal do IBOVESPA
    """
    # Convertendo datas para o formato aceito pelo YFinance
    data_inicio_obj = datetime.strptime(data_inicio, '%d/%m/%Y')
    data_fim_obj = datetime.strptime(data_fim, '%d/%m/%Y')
    
    # Obtendo dados do IBOVESPA (^BVSP)
    ibov = yf.download('^BVSP', start=data_inicio_obj, end=data_fim_obj, interval='1mo')
    
    # Calculando a variação percentual mensal
    ibov['Retorno'] = ibov['Close'].pct_change() * 100
    
    # Criando DataFrame no formato compatível com o resto do código
    df_ibovespa = pd.DataFrame({
        'ano_mes': ibov.index.strftime('%Y-%m'),
        'valor': ibov['Retorno']
    })
    
    # Removendo a primeira linha que terá NaN devido ao cálculo de retorno
    df_ibovespa = df_ibovespa.dropna()
    
    return df_ibovespa 