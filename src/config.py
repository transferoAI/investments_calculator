"""
Configurações do projeto de Calculadora de Investimentos.

Este módulo contém as configurações globais do projeto.
"""

import os
from typing import Dict

# Configurações de ambiente
class Config:
    """Classe de configuração."""
    
    def __init__(self):
        """Inicializa as configurações."""
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = self.environment == "development"
        
    @property
    def api_endpoints(self) -> Dict[str, str]:
        """Retorna os endpoints das APIs."""
        return {
            "bcb": "https://api.bcb.gov.br/",
            "yfinance": "https://query1.finance.yahoo.com/"
        }
    
    @property
    def default_values(self) -> Dict[str, float]:
        """Retorna os valores padrão para cálculos."""
        return {
            "taxa_inflacao": 2.5,
            "taxa_risco": 5.0,
            "capital_inicial": 10000.0
        }

# Instância única de configuração
config = Config()
