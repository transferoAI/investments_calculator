"""
Exceções personalizadas para o projeto de Calculadora de Investimentos.

Este módulo define as exceções específicas do domínio do projeto.
Cada exceção representa um tipo específico de erro que pode ocorrer
durante a execução do sistema.

Estrutura:
1. InvestmentError: Classe base para todas as exceções do projeto
2. CalculationError: Erros relacionados a cálculos
3. APIError: Erros relacionados a APIs externas
4. ValidationError: Erros de validação de dados
5. PersistenceError: Erros de persistência de dados
6. ExportError: Erros de exportação de dados

IMPORTANTE:
- Todas as exceções devem herdar de InvestmentError
- Mensagens de erro devem ser claras e informativas
- Incluir contexto relevante nos atributos da exceção
- Documentar quando cada exceção deve ser lançada
"""

from typing import Dict, List, Optional, TypedDict, Union, Any, Callable

class InvestmentError(Exception):
    """
    Classe base para todas as exceções do projeto.
    
    Esta exceção serve como base para todas as outras exceções
    específicas do domínio. Não deve ser lançada diretamente.
    
    Exemplo:
        class CustomError(InvestmentError):
            def __init__(self, message: str, context: Dict):
                super().__init__(message)
                self.context = context
    """
    
    def __init__(self, message: str):
        """
        Inicializa a exceção.
        
        Args:
            message (str): Mensagem descritiva do erro
        """
        super().__init__(message)
        self.message = message

class InvestmentCalculatorError(InvestmentError):
    """Exceção base para erros do projeto."""
    pass

class InvalidParameterError(InvestmentCalculatorError):
    """Exceção para parâmetros inválidos."""
    def __init__(self, parameter: str, message: str = ""):
        super().__init__(f"Parâmetro inválido: {parameter}. {message}")

class ThemeError(InvestmentCalculatorError):
    """
    Exceção para erros relacionados a temas e estilos.
    
    Esta exceção é lançada quando ocorre um erro durante
    a aplicação ou carregamento de temas e estilos.
    
    Exemplo:
        raise ThemeError(
            "Erro ao carregar arquivo de estilos",
            {"file_path": "styles.css", "error": "File not found"}
        )
    """
    
    def __init__(self, message: str, theme_context: dict = None):
        """
        Inicializa a exceção.
        
        Args:
            message (str): Mensagem descritiva do erro
            theme_context (dict, optional): Contexto do erro de tema
        """
        super().__init__(message)
        self.theme_context = theme_context or {}

class DataNotFoundError(InvestmentCalculatorError):
    """Exceção para dados não encontrados."""
    def __init__(self, data_type: str, message: str = ""):
        super().__init__(f"Dados não encontrados: {data_type}. {message}")

class CalculationError(InvestmentError):
    """
    Exceção para erros relacionados a cálculos.
    
    Esta exceção é lançada quando ocorre um erro durante
    a execução de cálculos financeiros.
    
    Exemplo:
        raise CalculationError(
            "Erro ao calcular rentabilidade",
            {"capital": 10000.0, "taxa": 0.1}
        )
    """
    
    def __init__(self, message: str, calculation_context: dict):
        """
        Inicializa a exceção.
        
        Args:
            message (str): Mensagem descritiva do erro
            calculation_context (dict): Contexto do cálculo que falhou
        """
        super().__init__(message)
        self.calculation_context = calculation_context

class APIError(InvestmentError):
    """
    Exceção para erros relacionados a APIs externas.
    
    Esta exceção é lançada quando ocorre um erro durante
    a comunicação com APIs externas.
    
    Exemplo:
        raise APIError(
            "Falha ao obter dados do BCB",
            {"endpoint": "/api/v1/indicadores", "status_code": 500}
        )
    """
    
    def __init__(self, message: str, api_context: dict):
        """
        Inicializa a exceção.
        
        Args:
            message (str): Mensagem descritiva do erro
            api_context (dict): Contexto da chamada à API que falhou
        """
        super().__init__(message)
        self.api_context = api_context

class ValidationError(InvestmentError):
    """
    Exceção para erros de validação de dados.
    
    Esta exceção é lançada quando os dados de entrada
    não atendem aos requisitos de validação.
    
    Exemplo:
        raise ValidationError(
            "Capital inicial inválido",
            {"field": "initial_capital", "value": -1000.0}
        )
    """
    
    def __init__(self, message: str, validation_context: dict):
        """
        Inicializa a exceção.
        
        Args:
            message (str): Mensagem descritiva do erro
            validation_context (dict): Contexto da validação que falhou
        """
        super().__init__(message)
        self.validation_context = validation_context

class PersistenceError(InvestmentError):
    """
    Exceção para erros de persistência de dados.
    
    Esta exceção é lançada quando ocorre um erro durante
    a persistência ou recuperação de dados.
    
    Exemplo:
        raise PersistenceError(
            "Falha ao salvar simulação",
            {"simulation_id": "sim_123", "operation": "save"}
        )
    """
    
    def __init__(self, message: str, persistence_context: dict):
        """
        Inicializa a exceção.
        
        Args:
            message (str): Mensagem descritiva do erro
            persistence_context (dict): Contexto da operação de persistência que falhou
        """
        super().__init__(message)
        self.persistence_context = persistence_context

class ExportError(InvestmentError):
    """
    Exceção para erros de exportação de dados.
    
    Esta exceção é lançada quando ocorre um erro durante
    a exportação de resultados.
    
    Exemplo:
        raise ExportError(
            "Falha ao exportar para CSV",
            {"format": "csv", "file_path": "/path/to/file.csv"}
        )
    """
    
    def __init__(self, message: str, export_context: dict):
        """
        Inicializa a exceção.
        
        Args:
            message (str): Mensagem descritiva do erro
            export_context (dict): Contexto da exportação que falhou
        """
        super().__init__(message)
        self.export_context = export_context
