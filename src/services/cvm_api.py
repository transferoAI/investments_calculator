import pandas as pd
import requests
import zipfile
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, TypedDict, Union, Any, Callable

from src.core.types import APIData
from src.core.interfaces import IInvestmentDataFetcher
from src.core.exceptions import APIError

from src.utils.logging import get_logger

class CVMDataFetcher(IInvestmentDataFetcher):
    """Classe para obtenção de dados da CVM."""
    
    def __init__(self):
        """Inicializa o fetcher."""
        self.base_url = "https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS"
        self.logger = get_logger(__name__)
    
    def fetch_data(self, indicators: List[str], end_date: datetime) -> Dict[str, APIData]:
        """
        Obtém dados dos indicadores da CVM.
        
        Args:
            indicators (List[str]): Lista de códigos dos fundos
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
                
                # Obtendo os dados da CVM
                url = f"https://api.cvm.gov.br/fundos/{indicator}/rentabilidade"
                params = {
                    "dataInicial": start_date.strftime("%Y-%m-%d"),
                    "dataFinal": end_date.strftime("%Y-%m-%d")
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = pd.DataFrame(response.json())
                
                if not data.empty:
                    # Calculando o retorno mensal
                    data['retorno'] = data['rentabilidade'].pct_change() * 100
                    
                    # Removendo a primeira linha (NaN)
                    data = data.dropna()
                    
                    # Adicionando a coluna de índice para referência
                    data['index'] = pd.to_datetime(data['data'])
                    
                    # Salvando os dados
                    results[indicator] = data
                
            except Exception as e:
                self.logger.error(f"Erro ao obter dados da CVM para {indicator}: {str(e)}")
                raise APIError(
                    f"Erro ao obter dados da CVM para {indicator}",
                    {"indicator": indicator, "params": params, "error": str(e)}
                )
        
        return results 