"""
Interfaces para o projeto de Calculadora de Investimentos.

Este módulo define as interfaces principais do projeto seguindo os princípios da Clean Architecture.
Cada interface define um contrato que deve ser implementado pelas camadas externas.

Estrutura:
1. IInvestmentCalculator: Interface para cálculos de investimento
2. IInvestmentDataFetcher: Interface para obtenção de dados
3. ISimulationHistory: Interface para histórico de simulações
4. IExportService: Interface para exportação de resultados
5. IUIComponent: Interface para componentes de interface

IMPORTANTE:
- Todas as interfaces devem ser abstratas (ABC)
- Cada interface deve ter apenas um propósito
- As implementações devem seguir o princípio de inversão de dependência
- As interfaces devem ser definidas em termos de domínio, não de implementação
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TypedDict, Union, Any, Callable
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
    """
    Interface para o cálculo de investimentos.
    
    Esta interface define o contrato para cálculo de rentabilidade de investimentos.
    Implementações devem seguir o princípio de responsabilidade única e
    não depender de detalhes de implementação externos.
    
    Exemplo de uso:
        class InvestmentCalculator(IInvestmentCalculator):
            def calculate(self, input_data: CalculationInput) -> CalculationOutput:
                # Implementação do cálculo
    """
    
    @abstractmethod
    def calculate(self, input_data: CalculationInput) -> CalculationOutput:
        """
        Calcula a rentabilidade do investimento.
        
        Args:
            input_data (CalculationInput): Dados de entrada para o cálculo
            
        Returns:
            CalculationOutput: Resultados do cálculo
            
        Raises:
            CalculationError: Se ocorrer erro no cálculo
        """
        pass

class IInvestmentDataFetcher(ABC):
    """
    Interface para obtenção de dados de investimento.
    
    Esta interface define o contrato para obtenção de dados de fontes externas.
    Implementações devem lidar com erros de API e retornar dados no formato esperado.
    
    Exemplo de uso:
        class BCBDataFetcher(IInvestmentDataFetcher):
            def fetch_data(self, indicators: List[str], end_date: datetime) -> Dict[str, APIData]:
                # Implementação da obtenção de dados
    """
    
    @abstractmethod
    def fetch_data(self, indicators: List[str], end_date: datetime) -> Dict[str, APIData]:
        """
        Obtém dados dos indicadores.
        
        Args:
            indicators (List[str]): Lista de códigos dos indicadores
            end_date (datetime): Data final para obtenção dos dados
            
        Returns:
            Dict[str, APIData]: Dicionário com os dados dos indicadores
            
        Raises:
            APIError: Se ocorrer erro na obtenção dos dados
        """
        pass

class ISimulationHistory(ABC):
    """
    Interface para histórico de simulações.
    
    Esta interface define o contrato para persistência e recuperação de simulações.
    Implementações devem garantir a integridade dos dados e fornecer estatísticas.
    
    Exemplo de uso:
        class SimulationHistory(ISimulationHistory):
            def add_simulation(self, simulation: HistoricalSimulation) -> None:
                # Implementação da persistência
    """
    
    @abstractmethod
    def add_simulation(self, simulation: HistoricalSimulation) -> None:
        """
        Adiciona uma simulação ao histórico.
        
        Args:
            simulation (HistoricalSimulation): Simulação a ser adicionada
            
        Raises:
            PersistenceError: Se ocorrer erro na persistência
        """
        pass
    
    @abstractmethod
    def get_history(self, limit: Optional[int] = None) -> List[HistoricalSimulation]:
        """
        Obtém o histórico de simulações.
        
        Args:
            limit (Optional[int]): Limite de simulações a retornar
            
        Returns:
            List[HistoricalSimulation]: Lista de simulações históricas
        """
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, float]:
        """
        Obtém estatísticas do histórico.
        
        Returns:
            Dict[str, float]: Estatísticas do histórico
        """
        pass

class IExportService(ABC):
    """
    Interface para serviços de exportação.
    
    Esta interface define o contrato para exportação de resultados.
    Implementações devem suportar diferentes formatos e garantir a integridade dos dados.
    
    Exemplo de uso:
        class CSVExportService(IExportService):
            def export_results(self, results: CalculationOutput, format: str) -> None:
                # Implementação da exportação
    """
    
    @abstractmethod
    def export_results(self, results: CalculationOutput, format: str) -> None:
        """
        Exporta os resultados.
        
        Args:
            results (CalculationOutput): Resultados a serem exportados
            format (str): Formato de exportação
            
        Raises:
            ExportError: Se ocorrer erro na exportação
        """
        pass

class IUIComponent(ABC):
    """
    Interface para componentes de interface.
    
    Esta interface define o contrato para componentes de interface do usuário.
    Implementações devem ser independentes da lógica de negócio e focar na apresentação.
    
    Exemplo de uso:
        class ResultsComponent(IUIComponent):
            def render(self, data: Optional[Dict] = None) -> None:
                # Implementação da renderização
    """
    
    @abstractmethod
    def render(self, data: Optional[Dict] = None) -> None:
        """
        Renderiza o componente.
        
        Args:
            data (Optional[Dict]): Dados a serem renderizados
        """
        pass
