"""
Exceções personalizadas para o projeto de Calculadora de Investimentos.
"""

class InvestmentCalculatorError(Exception):
    """Exceção base para erros do projeto."""
    pass

class InvalidParameterError(InvestmentCalculatorError):
    """Exceção para parâmetros inválidos."""
    def __init__(self, parameter: str, message: str = ""):
        super().__init__(f"Parâmetro inválido: {parameter}. {message}")

class DataNotFoundError(InvestmentCalculatorError):
    """Exceção para dados não encontrados."""
    def __init__(self, data_type: str, message: str = ""):
        super().__init__(f"Dados não encontrados: {data_type}. {message}")

class CalculationError(InvestmentCalculatorError):
    """Exceção para erros de cálculo."""
    def __init__(self, message: str = ""):
        super().__init__(f"Erro de cálculo. {message}")

class APIError(InvestmentCalculatorError):
    """Exceção para erros de API."""
    def __init__(self, api: str, message: str = ""):
        super().__init__(f"Erro na API {api}. {message}")
