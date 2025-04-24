import yfinance as yf
import pandas as pd
from datetime import datetime

def obter_dados_yfinance(simbolo, data_inicio, data_fim):
    """
    Obtém dados de um ativo financeiro via YFinance.
    
    Args:
        simbolo (str): Símbolo do ativo no YFinance (ex: '^BVSP' para IBOVESPA)
        data_inicio (str): Data inicial no formato DD/MM/YYYY
        data_fim (str): Data final no formato DD/MM/YYYY
        
    Returns:
        pandas.DataFrame: DataFrame com os dados do ativo contendo as colunas:
            - ano_mes: Mês no formato YYYY-MM
            - valor: Variação percentual mensal do ativo
    """
    # Convertendo datas para o formato aceito pelo YFinance
    data_inicio_obj = datetime.strptime(data_inicio, '%d/%m/%Y')
    data_fim_obj = datetime.strptime(data_fim, '%d/%m/%Y')
    
    # Obtendo dados do ativo
    ativo = yf.download(simbolo, start=data_inicio_obj, end=data_fim_obj, interval='1mo')
    
    # Calculando a variação percentual mensal
    ativo['Retorno'] = ativo['Close'].pct_change() * 100
    
    # Criando DataFrame no formato compatível com o resto do código
    df_ativo = pd.DataFrame({
        'ano_mes': ativo.index.strftime('%Y-%m'),
        'valor': ativo['Retorno']
    })
    
    # Removendo a primeira linha que terá NaN devido ao cálculo de retorno
    df_ativo = df_ativo.dropna()
    
    return df_ativo

# Símbolos dos ativos para referência:
# IBOVESPA: ^BVSP
# S&P 500: ^GSPC
# Dólar (USD/BRL): BRL=X
# Ouro: GC=F 