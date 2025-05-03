"""
Serviço para obtenção de dados do Banco Central do Brasil (BCB).

Este módulo implementa a interface IInvestmentDataFetcher para obtenção
de dados do BCB através de sua API. O módulo é responsável por:

1. Obter dados de indicadores financeiros
2. Tratar erros de API
3. Converter dados para o formato padrão
4. Cache de dados para otimização

IMPORTANTE:
- Tratamento adequado de erros de API
- Validação de dados recebidos
- Cache inteligente para evitar chamadas desnecessárias
- Documentação clara dos métodos e parâmetros
"""

import requests
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, TypedDict, Union, Any, Callable
from ..core.interfaces import IInvestmentDataFetcher
from ..core.types import APIData, IndicatorData
from ..core.exceptions import APIError
from ..utils.logging import get_logger

logger = get_logger(__name__)

class BCBDataFetcher(IInvestmentDataFetcher):
    """
    Implementação do serviço de obtenção de dados do BCB.
    
    Esta classe implementa a interface IInvestmentDataFetcher para
    obtenção de dados do Banco Central do Brasil através de sua API.
    
    Exemplo:
        fetcher = BCBDataFetcher()
        data = fetcher.fetch_data(
            indicators=["SELIC", "IPCA"],
            end_date=datetime.now()
        )
    """
    
    def __init__(self):
        """
        Inicializa o serviço.
        
        Configura a URL base da API e os códigos dos indicadores.
        """
        self.base_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
        self.indicators = {
            "SELIC": 11,  # Taxa Selic
            "IPCA": 433,  # IPCA
            "CDI": 12,    # CDI
            "IGPM": 189,  # IGP-M
            "PIB": 7326   # PIB
        }
        self._cache = {}  # Cache para otimizar chamadas à API
    
    def fetch_data(
        self,
        indicators: List[str],
        end_date: datetime
    ) -> Dict[str, APIData]:
        """
        Obtém dados dos indicadores do BCB.
        
        Esta função obtém dados dos indicadores especificados
        até a data final informada.
        
        Args:
            indicators (List[str]): Lista de códigos dos indicadores
            end_date (datetime): Data final para obtenção dos dados
            
        Returns:
            Dict[str, APIData]: Dicionário com os dados dos indicadores
            
        Raises:
            APIError: Se ocorrer erro na obtenção dos dados
            
        Exemplo:
            data = fetcher.fetch_data(
                indicators=["SELIC", "IPCA"],
                end_date=datetime.now()
            )
        """
        
        try:
            results = {}
            
            for indicator in indicators:
                if indicator not in self.indicators:
                    logger.warning(f"Indicador {indicator} não encontrado")
                    continue
                
                # Verifica cache
                cache_key = f"{indicator}_{end_date.strftime('%Y-%m-%d')}"
                if cache_key in self._cache:
                    results[indicator] = self._cache[cache_key]
                    continue
                
                # Obtém dados da API
                data = self._fetch_indicator_data(
                    self.indicators[indicator],
                    end_date
                )
                
                # Converte para o formato padrão
                api_data = self._convert_to_standard_format(
                    indicator,
                    data
                )
                
                # Armazena no cache
                self._cache[cache_key] = api_data
                results[indicator] = api_data
            
            return results
            
        except Exception as e:
            raise APIError(
                f"Erro ao obter dados do BCB: {str(e)}",
                {
                    "indicators": indicators,
                    "end_date": end_date
                }
            )
    
    def _fetch_indicator_data(
        self,
        indicator_code: int,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Obtém dados de um indicador específico.
        
        Esta função faz a chamada à API do BCB para obter
        dados de um indicador específico.
        
        Args:
            indicator_code (int): Código do indicador no BCB
            end_date (datetime): Data final para obtenção dos dados
            
        Returns:
            pd.DataFrame: DataFrame com os dados do indicador
            
        Raises:
            APIError: Se ocorrer erro na chamada à API
        """
        
        try:
            # Constrói a URL da API
            url = f"{self.base_url}/{indicator_code}/dados"
            
            # Define os parâmetros da requisição
            params = {
                "formato": "json",
                "dataInicial": "01/01/2000",  # Data inicial fixa
                "dataFinal": end_date.strftime("%d/%m/%Y")
            }
            
            # Faz a requisição
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Converte para DataFrame
            data = pd.DataFrame(response.json())
            data["data"] = pd.to_datetime(data["data"], format="%d/%m/%Y")
            data = data.sort_values("data")
            
            return data
            
        except requests.exceptions.RequestException as e:
            raise APIError(
                f"Erro na chamada à API do BCB: {str(e)}",
                {
                    "indicator_code": indicator_code,
                    "end_date": end_date,
                    "url": url,
                    "params": params
                }
            )
    
    def _convert_to_standard_format(
        self,
        indicator: str,
        data: pd.DataFrame
    ) -> APIData:
        """
        Converte dados para o formato padrão.
        
        Esta função converte os dados obtidos da API do BCB
        para o formato padrão definido no projeto.
        
        Args:
            indicator (str): Nome do indicador
            data (pd.DataFrame): Dados do indicador
            
        Returns:
            APIData: Dados no formato padrão
        """
        
        indicator_data = IndicatorData(
            code=indicator,
            name=self._get_indicator_name(indicator),
            values=data["valor"].tolist(),
            dates=data["data"].tolist()
        )
        
        return APIData(
            source="BCB",
            indicator=indicator,
            data=indicator_data,
            last_update=datetime.now()
        )
    
    def _get_indicator_name(self, indicator: str) -> str:
        """
        Obtém o nome completo do indicador.
        
        Esta função retorna o nome completo do indicador
        a partir do seu código.
        
        Args:
            indicator (str): Código do indicador
            
        Returns:
            str: Nome completo do indicador
        """
        
        names = {
            "SELIC": "Taxa Selic",
            "IPCA": "Índice Nacional de Preços ao Consumidor Amplo",
            "CDI": "Certificado de Depósito Interbancário",
            "IGPM": "Índice Geral de Preços do Mercado",
            "PIB": "Produto Interno Bruto"
        }
        
        return names.get(indicator, indicator) 