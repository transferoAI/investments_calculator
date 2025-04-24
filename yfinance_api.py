###############################################################################
# API de Integração com o Yahoo Finance
###############################################################################
# Este módulo é responsável por:
# 1. Obter dados históricos de ativos financeiros
# 2. Calcular retornos mensais
# 3. Processar e formatar dados para uso na aplicação
###############################################################################

# Importações necessárias
import yfinance as yf
import pandas as pd
from datetime import date, datetime, timedelta

def obter_dados_yfinance(simbolo, data_fim):
    """
    Obtém dados históricos e calcula retornos mensais de um ativo do Yahoo Finance.
    
    Args:
        simbolo (str): Símbolo do ativo no Yahoo Finance (ex: ^BVSP para IBOVESPA)
        data_fim (date): Data final para obtenção dos dados
    
    Returns:
        pd.DataFrame: DataFrame com os dados do ativo contendo:
            - index: Datas dos valores (datetime)
            - Open: Preço de abertura
            - High: Preço máximo
            - Low: Preço mínimo
            - Close: Preço de fechamento
            - Volume: Volume negociado
            - retorno: Retorno mensal em percentual
            - index: Referência temporal para join com outros dados
            
    Processo:
        1. Calcula a data inicial (5 anos antes da data final)
        2. Obtém dados históricos do Yahoo Finance
        3. Calcula retornos mensais
        4. Remove dados inválidos (NaN)
        5. Adiciona coluna de referência temporal
        
    Observações:
        - Utiliza a biblioteca yfinance para acesso aos dados
        - Dados são obtidos em frequência mensal
        - Retornos são calculados usando preços de fechamento
        - Em caso de erro, retorna None e imprime mensagem de erro
        
    Símbolos comuns:
        - IBOVESPA: ^BVSP
        - S&P 500: ^GSPC
        - Dólar (USD/BRL): BRL=X
        - Ouro: GC=F
    """
    # Calculando a data inicial (5 anos atrás)
    data_inicio = data_fim - timedelta(days=5*365)
    
    try:
        # Obtendo os dados do Yahoo Finance
        ticker = yf.Ticker(simbolo)
        dados = ticker.history(
            start=data_inicio,
            end=data_fim,
            interval='1mo'  # Dados mensais
        )
        
        # Calculando o retorno mensal em percentual
        dados['retorno'] = dados['Close'].pct_change() * 100
        
        # Removendo a primeira linha (NaN do primeiro retorno)
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