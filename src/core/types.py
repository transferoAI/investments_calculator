"""
Tipos personalizados para o projeto de Calculadora de Investimentos.

Este módulo define os tipos de dados utilizados em todo o projeto.
Os tipos são definidos usando TypedDict para garantir tipagem estática e
documentação clara da estrutura dos dados.

Estrutura:
1. SimulationParameters: Parâmetros de entrada para simulações
2. SimulationResults: Resultados de simulações
3. IndicatorData: Dados de indicadores financeiros
4. HistoricalSimulation: Simulação histórica
5. APIData: Dados retornados por APIs
6. CalculationInput: Entrada para cálculos
7. CalculationOutput: Saída de cálculos

IMPORTANTE:
- Todos os tipos devem ser imutáveis
- Campos obrigatórios devem ser documentados
- Tipos devem refletir o domínio do negócio
- Evitar tipos complexos aninhados
"""

from typing import Dict, List, Optional, TypedDict, Union, Any, Callable
from datetime import datetime
import pandas as pd

class SimulationParameters(TypedDict):
    """
    Parâmetros de entrada para simulações.
    
    Este tipo define os parâmetros necessários para realizar uma simulação
    de investimento. Todos os campos são obrigatórios e devem ser validados
    antes do uso.
    
    Exemplo:
        params = SimulationParameters(
            initial_capital=10000.0,
            monthly_contribution=1000.0,
            monthly_withdrawal=0.0,
            inflation_rate=0.05,
            risk_free_rate=0.10,
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2023, 1, 1),
            indicators=["BCB:SELIC", "BCB:IPCA"]
        )
    """
    
    initial_capital: float  # Capital inicial do investimento
    monthly_contribution: float  # Contribuição mensal
    monthly_withdrawal: float  # Saque mensal
    inflation_rate: float  # Taxa de inflação anual
    risk_free_rate: float  # Taxa livre de risco anual
    start_date: datetime  # Data inicial da simulação
    end_date: datetime  # Data final da simulação
    indicators: List[str]  # Lista de indicadores para comparação

class SimulationResults(TypedDict):
    """
    Resultados de simulações.
    
    Este tipo define os resultados calculados de uma simulação de investimento.
    Inclui métricas financeiras e estatísticas importantes para análise.
    
    Exemplo:
        results = SimulationResults(
            final_capital=15000.0,
            total_profitability=0.5,
            annualized_profitability=0.15,
            volatility=0.2,
            sharpe_index=0.75,
            monthly_evolution=[10000.0, 11000.0, 12000.0, 13000.0, 14000.0, 15000.0],
            monthly_profitability=[0.1, 0.09, 0.08, 0.07, 0.07]
        )
    """
    
    final_capital: float  # Capital final do investimento
    total_profitability: float  # Rentabilidade total
    annualized_profitability: float  # Rentabilidade anualizada
    volatility: float  # Volatilidade do investimento
    sharpe_index: float  # Índice de Sharpe
    monthly_evolution: List[float]  # Evolução mensal do capital
    monthly_profitability: List[float]  # Rentabilidade mensal

class IndicatorData(TypedDict):
    """
    Dados de indicadores financeiros.
    
    Este tipo define a estrutura dos dados de indicadores financeiros
    obtidos de fontes externas. Inclui valores e datas de referência.
    
    Exemplo:
        indicator = IndicatorData(
            code="SELIC",
            name="Taxa Selic",
            values=[0.135, 0.13, 0.125],
            dates=[datetime(2023, 1, 1), datetime(2023, 2, 1), datetime(2023, 3, 1)]
        )
    """
    
    code: str  # Código do indicador
    name: str  # Nome do indicador
    values: List[float]  # Valores do indicador
    dates: List[datetime]  # Datas dos valores

class HistoricalSimulation(TypedDict):
    """
    Simulação histórica.
    
    Este tipo define uma simulação completa, incluindo parâmetros
    de entrada e resultados calculados. Usado para persistência e
    histórico de simulações.
    
    Exemplo:
        simulation = HistoricalSimulation(
            id="sim_123",
            timestamp=datetime.now(),
            parameters=params,
            results=results
        )
    """
    
    id: str  # Identificador único da simulação
    timestamp: datetime  # Data e hora da simulação
    parameters: SimulationParameters  # Parâmetros utilizados
    results: SimulationResults  # Resultados obtidos

class APIData(TypedDict):
    """
    Dados retornados por APIs.
    
    Este tipo define a estrutura dos dados retornados por APIs externas.
    Inclui metadados e valores processados.
    
    Exemplo:
        api_data = APIData(
            source="BCB",
            indicator="SELIC",
            data=indicator,
            last_update=datetime.now()
        )
    """
    
    source: str  # Fonte dos dados
    indicator: str  # Indicador financeiro
    data: IndicatorData  # Dados do indicador
    last_update: datetime  # Última atualização

class CalculationInput(TypedDict):
    """
    Entrada para cálculos.
    
    Este tipo define os dados necessários para realizar cálculos
    de investimento. Combina parâmetros de simulação com dados
    de indicadores.
    
    Exemplo:
        input_data = CalculationInput(
            parameters=params,
            indicators_data={"SELIC": api_data}
        )
    """
    
    parameters: SimulationParameters  # Parâmetros da simulação
    indicators_data: Dict[str, APIData]  # Dados dos indicadores

class CalculationOutput(TypedDict):
    """
    Saída de cálculos.
    
    Este tipo define os resultados de cálculos de investimento.
    Inclui métricas financeiras e dados processados.
    
    Exemplo:
        output_data = CalculationOutput(
            results=results,
            processed_data={"monthly_evolution": monthly_data}
        )
    """
    
    results: SimulationResults  # Resultados da simulação
    processed_data: Dict[str, List[float]]  # Dados processados
