"""
Tipos personalizados para o projeto de Calculadora de Investimentos.
"""

from typing import Dict, List, Optional, TypedDict, Union
from datetime import datetime
import pandas as pd

class SimulationParameters(TypedDict):
    """Parâmetros de uma simulação."""
    capital_inicial: float
    retirada_mensal: float
    aporte_mensal: float
    data_fim: datetime
    reinvestir: bool
    taxa_inflacao: float
    taxa_risco: float

class SimulationResults(TypedDict):
    """Resultados de uma simulação."""
    capital_final: float
    rentabilidade_total: float
    volatilidade: float
    indice_sharpe: float

class IndicatorData(TypedDict):
    """Dados de um indicador."""
    nome: str
    tipo: str
    valor: float
    data: datetime

class HistoricalSimulation(TypedDict):
    """Simulação histórica."""
    data: str
    parametros: SimulationParameters
    resultados: SimulationResults
    indicadores: List[str]

class APIData(TypedDict):
    """Dados de API."""
    nome: str
    valor: float
    data: datetime
    fonte: str

class CalculationInput(TypedDict):
    """Entrada para cálculo."""
    capital_investido: float
    retirada_mensal: float
    aporte_mensal: float
    data_fim: datetime
    reinvestir: bool
    indicadores_selecionados: List[str]
    mostrar_tendencias: bool
    mostrar_estatisticas: bool

class CalculationOutput(TypedDict):
    """Saída do cálculo."""
    df_resultado: pd.DataFrame
    indicadores_selecionados: List[str]
    mostrar_tendencias: bool
    mostrar_estatisticas: bool
