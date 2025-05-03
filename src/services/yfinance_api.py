import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, TypedDict, Union, Any, Callable

from src.core.types import APIData
from src.core.interfaces import IInvestmentDataFetcher
from src.core.exceptions import APIError

from src.utils.logging import get_logger

class YFinanceDataFetcher(IInvestmentDataFetcher):
    """Classe para obtenção de dados do Yahoo Finance."""
    
    def __init__(self):
        """Inicializa o fetcher."""
        self.logger = get_logger(__name__)
    
    def fetch_data(self, indicators: List[str], end_date: datetime) -> Dict[str, APIData]:
        """
        Obtém dados dos indicadores do Yahoo Finance.
        
        Args:
            indicators (List[str]): Lista de símbolos dos ativos
            end_date (datetime): Data final para obtenção dos dados
            
        Returns:
            Dict[str, APIData]: Dicionário com os dados dos indicadores
            
        Raises:
            APIError: Se ocorrer erro na obtenção dos dados
        """
        results = {}
        
        for indicator in indicators:
            try:
                # Calculando a data inicial (5 anos atrás)
                start_date = end_date - timedelta(days=5*365)
                
                # Obtendo os dados do Yahoo Finance
                ticker = yf.Ticker(indicator)
                data = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval='1mo'
                )
                
                if not data.empty:
                    # Calculando o retorno mensal
                    data['retorno'] = data['Close'].pct_change() * 100
                    
                    # Removendo a primeira linha (NaN)
                    data = data.dropna()
                    
                    # Adicionando a coluna de índice para referência
                    data['index'] = data.index
                    
                    # Salvando os dados
                    results[indicator] = data
                
            except Exception as e:
                self.logger.error(f"Erro ao obter dados do Yahoo Finance para {indicator}: {str(e)}")
                raise APIError(f"Erro ao obter dados do Yahoo Finance para {indicator}")
        
        return results 