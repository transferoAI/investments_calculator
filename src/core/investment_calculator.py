###############################################################################
# Módulo de Cálculo de Rentabilidade
###############################################################################
# Este módulo é responsável por:
# 1. Calcular a rentabilidade de investimentos ao longo do tempo
# 2. Simular cenários com aportes e retiradas
# 3. Integrar dados de diferentes indicadores financeiros
###############################################################################

# Importações necessárias
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, TypedDict, Union, Any, Callable
from .types import (
    SimulationParameters,
    SimulationResults,
    CalculationInput,
    CalculationOutput
)
from .exceptions import CalculationError, ValidationError
from .interfaces import IInvestmentCalculator

class InvestmentCalculator(IInvestmentCalculator):
    """
    Implementação do calculador de investimentos.
    
    Esta classe implementa a interface IInvestmentCalculator e é responsável
    por realizar todos os cálculos relacionados a investimentos.
    
    Exemplo:
        calculator = InvestmentCalculator()
        input_data = CalculationInput(...)
        results = calculator.calculate(input_data)
    """
    
    def calculate(self, input_data: CalculationInput) -> CalculationOutput:
        """
        Calcula a rentabilidade de um investimento.
        
        Args:
            input_data (CalculationInput): Dados de entrada para o cálculo
            
        Returns:
            CalculationOutput: Resultados do cálculo
            
        Raises:
            ValidationError: Se os dados de entrada forem inválidos
            CalculationError: Se ocorrer erro durante o cálculo
        """
        return calcular_rentabilidade(input_data)

def calcular_rentabilidade(input_data: CalculationInput) -> CalculationOutput:
    """
    Calcula a rentabilidade de um investimento.
    
    Esta função é o ponto de entrada principal para cálculos de investimento.
    Ela coordena todos os cálculos necessários e retorna os resultados
    em um formato padronizado.
    
    Args:
        input_data (CalculationInput): Dados de entrada para o cálculo
        
    Returns:
        CalculationOutput: Resultados do cálculo
        
    Raises:
        ValidationError: Se os dados de entrada forem inválidos
        CalculationError: Se ocorrer erro durante o cálculo
        
    Exemplo:
        input_data = CalculationInput(
            parameters={
                "initial_capital": 10000.0,
                "monthly_contribution": 1000.0,
                "monthly_withdrawal": 0.0,
                "inflation_rate": 0.05,
                "risk_free_rate": 0.10,
                "start_date": datetime(2020, 1, 1),
                "end_date": datetime(2023, 1, 1)
            },
            indicators_data={"SELIC": {...}}
        )
        results = calcular_rentabilidade(input_data)
    """
    
    try:
        # Validação dos dados de entrada
        _validar_dados_entrada(input_data)
        
        # Extração dos parâmetros
        params = input_data["parameters"]
        
        # Cálculo da evolução mensal do capital
        monthly_evolution = _calcular_evolucao_mensal(params)
        
        # Cálculo da rentabilidade mensal
        monthly_profitability = _calcular_rentabilidade_mensal(monthly_evolution)
        
        # Cálculo da rentabilidade total
        total_profitability = _calcular_rentabilidade_total(monthly_profitability)
        
        # Cálculo da rentabilidade anualizada
        annualized_profitability = _calcular_rentabilidade_anualizada(
            total_profitability,
            params["start_date"],
            params["end_date"]
        )
        
        # Cálculo da volatilidade
        volatility = _calcular_volatilidade(monthly_profitability)
        
        # Cálculo do índice de Sharpe
        sharpe_index = _calcular_indice_sharpe(
            annualized_profitability,
            volatility,
            params["risk_free_rate"]
        )
        
        # Preparação dos resultados
        results = SimulationResults(
            final_capital=monthly_evolution[-1],
            total_profitability=total_profitability,
            annualized_profitability=annualized_profitability,
            volatility=volatility,
            sharpe_index=sharpe_index,
            monthly_evolution=monthly_evolution,
            monthly_profitability=monthly_profitability
        )
        
        # Preparação dos dados processados
        processed_data = {
            "monthly_evolution": monthly_evolution,
            "monthly_profitability": monthly_profitability
        }
        
        return CalculationOutput(
            results=results,
            processed_data=processed_data
        )
        
    except Exception as e:
        raise CalculationError(
            f"Erro ao calcular rentabilidade: {str(e)}",
            {"input_data": input_data}
        )

def _validar_dados_entrada(input_data: CalculationInput) -> None:
    """
    Valida os dados de entrada para o cálculo.
    
    Esta função verifica se todos os parâmetros necessários estão presentes
    e se seus valores são válidos.
    
    Args:
        input_data (CalculationInput): Dados de entrada a serem validados
        
    Raises:
        ValidationError: Se os dados forem inválidos
    """
    
    params = input_data["parameters"]
    
    # Validação do capital inicial
    if params["initial_capital"] <= 0:
        raise ValidationError(
            "Capital inicial deve ser maior que zero",
            {"field": "initial_capital", "value": params["initial_capital"]}
        )
    
    # Validação das datas
    if params["start_date"] >= params["end_date"]:
        raise ValidationError(
            "Data inicial deve ser anterior à data final",
            {
                "start_date": params["start_date"],
                "end_date": params["end_date"]
            }
        )
    
    # Validação das taxas
    if params["inflation_rate"] < 0:
        raise ValidationError(
            "Taxa de inflação não pode ser negativa",
            {"field": "inflation_rate", "value": params["inflation_rate"]}
        )
    
    if params["risk_free_rate"] < 0:
        raise ValidationError(
            "Taxa livre de risco não pode ser negativa",
            {"field": "risk_free_rate", "value": params["risk_free_rate"]}
        )

def _calcular_evolucao_mensal(params: SimulationParameters) -> List[float]:
    """
    Calcula a evolução mensal do capital.
    
    Esta função simula a evolução do capital ao longo do tempo,
    considerando aportes e retiradas mensais.
    
    Args:
        params (SimulationParameters): Parâmetros da simulação
        
    Returns:
        List[float]: Lista com a evolução mensal do capital
    """
    
    capital = params["initial_capital"]
    evolution = [capital]
    
    current_date = params["start_date"]
    while current_date < params["end_date"]:
        # Aplica aporte mensal
        capital += params["monthly_contribution"]
        
        # Aplica retirada mensal
        capital -= params["monthly_withdrawal"]
        
        # Aplica rentabilidade mensal (simplificado)
        capital *= (1 + params["risk_free_rate"] / 12)
        
        evolution.append(capital)
        current_date += timedelta(days=30)
    
    return evolution

def _calcular_rentabilidade_mensal(evolution: List[float]) -> List[float]:
    """
    Calcula a rentabilidade mensal.
    
    Esta função calcula a rentabilidade mensal a partir da
    evolução do capital.
    
    Args:
        evolution (List[float]): Evolução mensal do capital
        
    Returns:
        List[float]: Lista com a rentabilidade mensal
    """
    
    profitability = []
    for i in range(1, len(evolution)):
        monthly_return = (evolution[i] - evolution[i-1]) / evolution[i-1]
        profitability.append(monthly_return)
    
    return profitability

def _calcular_rentabilidade_total(monthly_profitability: List[float]) -> float:
    """
    Calcula a rentabilidade total.
    
    Esta função calcula a rentabilidade total acumulada
    a partir das rentabilidades mensais.
    
    Args:
        monthly_profitability (List[float]): Rentabilidade mensal
        
    Returns:
        float: Rentabilidade total
    """
    
    return (1 + np.prod([1 + r for r in monthly_profitability])) - 1

def _calcular_rentabilidade_anualizada(
    total_profitability: float,
    start_date: datetime,
    end_date: datetime
) -> float:
    """
    Calcula a rentabilidade anualizada.
    
    Esta função converte a rentabilidade total em uma
    taxa anual equivalente.
    
    Args:
        total_profitability (float): Rentabilidade total
        start_date (datetime): Data inicial
        end_date (datetime): Data final
        
    Returns:
        float: Rentabilidade anualizada
    """
    
    years = (end_date - start_date).days / 365
    return (1 + total_profitability) ** (1 / years) - 1

def _calcular_volatilidade(monthly_profitability: List[float]) -> float:
    """
    Calcula a volatilidade.
    
    Esta função calcula o desvio padrão das rentabilidades
    mensais, que representa a volatilidade do investimento.
    
    Args:
        monthly_profitability (List[float]): Rentabilidade mensal
        
    Returns:
        float: Volatilidade
    """
    
    return np.std(monthly_profitability) * np.sqrt(12)

def _calcular_indice_sharpe(
    annualized_profitability: float,
    volatility: float,
    risk_free_rate: float
) -> float:
    """
    Calcula o índice de Sharpe.
    
    Esta função calcula o índice de Sharpe, que mede o
    retorno ajustado ao risco do investimento.
    
    Args:
        annualized_profitability (float): Rentabilidade anualizada
        volatility (float): Volatilidade
        risk_free_rate (float): Taxa livre de risco
        
    Returns:
        float: Índice de Sharpe
    """
    
    if volatility == 0:
        return 0
    
    return (annualized_profitability - risk_free_rate) / volatility 