"""
Interfaces para o projeto de Calculadora de Investimentos.

Este módulo define as interfaces principais do projeto.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from .types import (
    SimulationParameters,
    SimulationResults,
    HistoricalSimulation,
    APIData,
    CalculationInput,
    CalculationOutput
)

class IInvestmentCalculator(ABC):
    """Interface para o cálculo de investimentos."""
    
    @abstractmethod
    def calculate(self, input_data: CalculationInput) -> CalculationOutput:
        """Calcula a rentabilidade do investimento."""
        pass

class IInvestmentDataFetcher(ABC):
    """Interface para obtenção de dados de investimento."""
    
    @abstractmethod
    def fetch_data(self, indicators: List[str], end_date: datetime) -> Dict[str, APIData]:
        """Obtém dados dos indicadores."""
        pass

class ISimulationHistory(ABC):
    """Interface para histórico de simulações."""
    
    @abstractmethod
    def add_simulation(self, simulation: HistoricalSimulation) -> None:
        """Adiciona uma simulação ao histórico."""
        pass
    
    @abstractmethod
    def get_history(self, limit: Optional[int] = None) -> List[HistoricalSimulation]:
        """Obtém o histórico de simulações."""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, float]:
        """Obtém estatísticas do histórico."""
        pass

class IExportService(ABC):
    """Interface para serviços de exportação."""
    
    @abstractmethod
    def export_results(self, results: CalculationOutput, format: str) -> None:
        """Exporta os resultados."""
        pass

class IUIComponent(ABC):
    """Interface para componentes de interface."""
    
    @abstractmethod
    def render(self, data: Optional[Dict] = None) -> None:
        """Renderiza o componente."""
        pass
