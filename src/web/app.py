"""
Aplicação principal da Calculadora de Investimentos.

Este módulo implementa a aplicação principal usando Streamlit.
O módulo é responsável por:

1. Coordenar todos os componentes
2. Gerenciar o estado da aplicação
3. Processar os dados de entrada
4. Exibir os resultados

Estrutura do módulo:
1. Configuração Inicial
   - Importações
   - Configuração de logging
2. Função Principal
   - Inicialização de componentes
   - Fluxo de dados
   - Tratamento de erros

IMPORTANTE:
- Fluxo de dados claro e organizado
- Tratamento adequado de erros
- Feedback ao usuário
- Performance otimizada
- Documentação clara para facilitar manutenção

TODO:
- Implementar cache para dados de API
- Adicionar persistência de estado
- Melhorar tratamento de erros
- Adicionar testes automatizados
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, TypedDict, Union, Tuple
import logging

from src.core.investment_calculator import calcular_rentabilidade, InvestmentCalculator
from src.services.bcb_api import BCBDataFetcher
from src.services.yfinance_api import YFinanceDataFetcher
from src.services.cvm_api import CVMDataFetcher
from src.core.types import CalculationInput, CalculationOutput, SimulationParameters
from src.core.exceptions import CalculationError
from src.core.interfaces import IInvestmentDataFetcher, IInvestmentCalculator
from src.core.data_fetcher import InvestmentDataFetcher
from src.web.ui_components import (
    ThemeComponent,
    InputFormComponent,
    DashboardComponent,
    formatar_moeda,
    formatar_percentual
)
from src.utils.logging import get_logger
from src.utils.cache import cache
from src.utils.state import state

# Configuração inicial
logger = get_logger(__name__)

def initialize_data_fetchers() -> Tuple[BCBDataFetcher, YFinanceDataFetcher, CVMDataFetcher]:
    """
    Inicializa os fetchers de dados.
    
    Returns:
        Tuple contendo os fetchers inicializados:
        - BCBDataFetcher: Para dados do Banco Central
        - YFinanceDataFetcher: Para dados do Yahoo Finance
        - CVMDataFetcher: Para dados da CVM
    """
    return (
        BCBDataFetcher(),
        YFinanceDataFetcher(),
        CVMDataFetcher()
    )

def fetch_indicators_data(
    bcb_fetcher: BCBDataFetcher,
    yfinance_fetcher: YFinanceDataFetcher,
    cvm_fetcher: CVMDataFetcher
) -> Dict[str, Dict]:
    """
    Obtém dados dos indicadores de todas as fontes.
    
    Args:
        bcb_fetcher: Fetcher para dados do BCB
        yfinance_fetcher: Fetcher para dados do YFinance
        cvm_fetcher: Fetcher para dados da CVM
        
    Returns:
        Dict com os dados dos indicadores
        
    TODO:
    - Implementar cache para os dados
    - Adicionar tratamento de erros específico
    - Melhorar a granularidade dos dados
    """
    indicators_data = {}
    
    try:
        # Dados do BCB
        bcb_data = bcb_fetcher.fetch_data(
            indicators=["SELIC", "IPCA"],
            end_date=datetime.now()
        )
        indicators_data.update(bcb_data)
        
        # Dados do YFinance
        yfinance_data = yfinance_fetcher.fetch_data(
            indicators=["^BVSP", "^GSPC"],
            end_date=datetime.now()
        )
        indicators_data.update(yfinance_data)
        
        # Dados da CVM
        cvm_data = cvm_fetcher.fetch_data(
            indicators=["CDI", "IPCA"],
            end_date=datetime.now()
        )
        indicators_data.update(cvm_data)
        
    except Exception as e:
        logger.error(f"Erro ao obter dados dos indicadores: {str(e)}")
        st.error("Erro ao obter dados dos indicadores. Algumas funcionalidades podem estar limitadas.")
    
    return indicators_data

def initialize_data_fetcher() -> IInvestmentDataFetcher:
    """
    Inicializa o data fetcher com cache.
    
    Returns:
        IInvestmentDataFetcher: Instância do data fetcher
    """
    return InvestmentDataFetcher(cache=cache)

def initialize_calculator() -> IInvestmentCalculator:
    """
    Inicializa o calculator.
    
    Returns:
        IInvestmentCalculator: Instância do calculator
    """
    return InvestmentCalculator()

def fetch_indicators_data_cached(
    data_fetcher: IInvestmentDataFetcher,
    indicators: list[str],
    start_date: datetime,
    end_date: datetime
) -> dict:
    """
    Busca dados dos indicadores com cache.
    
    Args:
        data_fetcher: Instância do data fetcher
        indicators: Lista de indicadores
        start_date: Data inicial
        end_date: Data final
        
    Returns:
        dict: Dados dos indicadores
    """
    try:
        # Tenta obter do cache primeiro
        cache_key = f"indicators_{start_date}_{end_date}_{'_'.join(indicators)}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("Dados obtidos do cache")
            return cached_data
        
        # Busca dados da API
        data = data_fetcher.fetch_data(indicators, start_date, end_date)
        
        # Armazena no cache
        cache.set(cache_key, data)
        
        return data
    except Exception as e:
        logger.error(f"Erro ao buscar dados: {str(e)}")
        raise

class MainApp:
    """
    Classe principal da aplicação.
    
    Esta classe é responsável por:
    1. Inicializar todos os componentes
    2. Gerenciar o estado da aplicação
    3. Coordenar o fluxo de dados
    4. Exibir a interface do usuário
    
    Exemplo:
        app = MainApp()
        app.run()
    """
    
    def __init__(self):
        """Inicializa a aplicação e seus componentes."""
        self.theme_component = ThemeComponent()
        self.input_form_component = InputFormComponent()
        self.dashboard_component = DashboardComponent()
        self.data_fetcher = initialize_data_fetcher()
        self.calculator = initialize_calculator()
        self.logger = get_logger(__name__)
    
    def run(self):
        """
        Executa a aplicação.
        
        Este método coordena todo o fluxo da aplicação:
        1. Configura o tema
        2. Obtém dados de entrada
        3. Processa os dados
        4. Exibe os resultados
        """
        try:
            # Configura o tema
            self.theme_component.render()
            
            # Obtém parâmetros do usuário
            params = self.input_form_component.render()
            
            if params:
                # Obtém dados dos indicadores
                indicators_data = fetch_indicators_data_cached(
                    self.data_fetcher,
                    params["indicators"],
                    params["start_date"],
                    params["end_date"]
                )
                
                # Prepara dados de entrada
                input_data = CalculationInput(
                    parameters=params,
                    indicators_data=indicators_data
                )
                
                # Calcula resultados
                results = self.calculator.calculate(input_data)
                
                # Exibe resultados
                self.dashboard_component.render(results)
                
        except Exception as e:
            self.logger.error(f"Erro na execução da aplicação: {str(e)}")
            st.error("Ocorreu um erro inesperado. Por favor, tente novamente.")

if __name__ == "__main__":
    app = MainApp()
    app.run()
