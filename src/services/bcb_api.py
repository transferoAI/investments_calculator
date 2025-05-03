import requests
from datetime import datetime, date
import pandas as pd
from typing import Dict, List, Optional

from src.core.types import APIData
from src.core.interfaces import IInvestmentDataFetcher
from src.core.exceptions import APIError

from src.utils.logging import project_logger

class BCBDataFetcher(IInvestmentDataFetcher):
    """Classe para obtenção de dados do Banco Central do Brasil."""
    
    def __init__(self):
        """Inicializa o fetcher."""
        self.base_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
        self.logger = project_logger
    
    def fetch_data(self, indicators: List[str], end_date: datetime) -> Dict[str, APIData]:
        """
        Obtém dados dos indicadores do BCB.
        
        Args:
            indicators (List[str]): Lista de códigos dos indicadores
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
                
                # Formatando as datas para o formato do BCB
                start_date_str = start_date.strftime('%d/%m/%Y')
                end_date_str = end_date.strftime('%d/%m/%Y')
                
                # Construindo a URL da API
                url = f'{self.base_url}/{indicator}/dados'
                params = {
                    'formato': 'json',
                    'dataInicial': start_date_str,
                    'dataFinal': end_date_str
                }
                
                # Fazendo a requisição
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                # Convertendo os dados para DataFrame
                data = pd.DataFrame(response.json())
                
                # Convertendo a coluna de data
                data['data'] = pd.to_datetime(data['data'], format='%d/%m/%Y')
                data.set_index('data', inplace=True)
                
                # Renomeando a coluna de valor
                data.rename(columns={'valor': 'valor'}, inplace=True)
                
                # Adicionando a coluna de índice para referência
                data['index'] = data.index
                
                # Salvando os dados
                results[indicator] = data
                
            except Exception as e:
                self.logger.error(f"Erro ao obter dados do BCB para {indicator}: {str(e)}")
                raise APIError(f"Erro ao obter dados do BCB para {indicator}")
        
        return results 