"""
Módulo de obtenção de dados de investimentos.

Este módulo implementa a classe principal para obtenção de dados
de diferentes fontes (BCB, Yahoo Finance, CVM).

Estrutura:
1. InvestmentDataFetcher: Classe principal que coordena a obtenção de dados
2. Integração com cache para otimização
3. Tratamento de erros e validações
4. Formatação padronizada dos dados

IMPORTANTE:
- Tratamento adequado de erros
- Cache inteligente para otimização
- Validação dos dados obtidos
- Documentação clara dos métodos
"""

from datetime import datetime
from typing import Dict, List, Optional, TypedDict, Union, Any, Callable
from .interfaces import IInvestmentDataFetcher
from .types import APIData
from .exceptions import APIError
from ..services.bcb_api import BCBDataFetcher
from ..services.yfinance_api import YFinanceDataFetcher
from ..services.cvm_api import CVMDataFetcher
from ..utils.logging import get_logger
from ..utils.cache import CacheManager

class InvestmentDataFetcher(IInvestmentDataFetcher):
    """
    Implementação do data fetcher principal.
    
    Esta classe coordena a obtenção de dados de diferentes fontes,
    implementando cache e tratamento de erros.
    
    Exemplo:
        fetcher = InvestmentDataFetcher(cache=cache_manager)
        data = fetcher.fetch_data(
            indicators=["SELIC", "IPCA"],
            end_date=datetime.now()
        )
    """
    
    def __init__(self, cache: Optional[CacheManager] = None):
        """
        Inicializa o data fetcher.
        
        Args:
            cache (Optional[CacheManager]): Gerenciador de cache
        """
        self.bcb_fetcher = BCBDataFetcher()
        self.yfinance_fetcher = YFinanceDataFetcher()
        self.cvm_fetcher = CVMDataFetcher()
        self.cache = cache
        self.logger = get_logger(__name__)
    
    def fetch_data(
        self,
        indicators: List[str],
        end_date: datetime
    ) -> Dict[str, APIData]:
        """
        Obtém dados dos indicadores.
        
        Esta função coordena a obtenção de dados de diferentes fontes,
        utilizando cache quando disponível.
        
        Args:
            indicators (List[str]): Lista de indicadores
            end_date (datetime): Data final
            
        Returns:
            Dict[str, APIData]: Dados dos indicadores
            
        Raises:
            APIError: Se ocorrer erro na obtenção dos dados
        """
        try:
            results = {}
            
            for indicator in indicators:
                # Tenta obter do cache primeiro
                if self.cache:
                    cache_key = f"indicator_{indicator}_{end_date}"
                    cached_data = self.cache.get(cache_key)
                    if cached_data:
                        self.logger.info(f"Dados obtidos do cache para {indicator}")
                        results[indicator] = cached_data
                        continue
                
                # Se não está no cache, busca da fonte apropriada
                if indicator.startswith("BCB:"):
                    data = self.bcb_fetcher.fetch_data([indicator[4:]], end_date)
                elif indicator.startswith("YF:"):
                    data = self.yfinance_fetcher.fetch_data([indicator[3:]], end_date)
                elif indicator.startswith("CVM:"):
                    data = self.cvm_fetcher.fetch_data([indicator[4:]], end_date)
                else:
                    raise APIError(f"Fonte desconhecida para o indicador: {indicator}")
                
                # Salva no cache se disponível
                if self.cache:
                    self.cache.set(cache_key, data)
                
                results.update(data)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados: {str(e)}")
            raise APIError(f"Erro ao obter dados dos indicadores: {str(e)}") 