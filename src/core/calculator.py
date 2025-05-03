"""
Calculadora de investimentos.

Este módulo implementa a lógica de cálculo
de rentabilidade de investimentos.

Estrutura:
1. InvestmentCalculator: Classe principal
2. Métodos de cálculo
3. Integração com cache

IMPORTANTE:
- Cache de resultados para performance
- Validação de parâmetros
- Tratamento de erros
- Logging detalhado
"""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from src.utils.cache import CacheManager
from src.utils.logging import get_logger
from src.core.interfaces import IInvestmentCalculator

logger = get_logger(__name__)

class InvestmentCalculator(IInvestmentCalculator):
    """Implementação da calculadora de investimentos."""
    
    def __init__(self, cache: Optional[CacheManager] = None):
        """
        Inicializa a calculadora.
        
        Args:
            cache: Gerenciador de cache (opcional)
        """
        self.cache = cache
    
    def calculate(
        self,
        initial_amount: float,
        monthly_amount: float,
        indicators: List[str],
        indicators_data: Dict
    ) -> Dict:
        """
        Calcula a rentabilidade do investimento.
        
        Args:
            initial_amount: Valor inicial
            monthly_amount: Valor mensal
            indicators: Lista de indicadores
            indicators_data: Dados dos indicadores
            
        Returns:
            Dict: Resultados do cálculo
        """
        try:
            # Gera chave de cache
            cache_key = self._generate_cache_key(
                initial_amount,
                monthly_amount,
                indicators,
                indicators_data
            )
            
            # Tenta obter do cache
            if self.cache:
                cached_results = self.cache.get(cache_key)
                if cached_results:
                    logger.info("Resultados obtidos do cache")
                    return cached_results
            
            # Valida parâmetros
            self._validate_parameters(
                initial_amount,
                monthly_amount,
                indicators,
                indicators_data
            )
            
            # Calcula resultados
            results = self._calculate_results(
                initial_amount,
                monthly_amount,
                indicators,
                indicators_data
            )
            
            # Armazena no cache
            if self.cache:
                self.cache.set(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao calcular rentabilidade: {str(e)}")
            raise
    
    def _generate_cache_key(
        self,
        initial_amount: float,
        monthly_amount: float,
        indicators: List[str],
        indicators_data: Dict
    ) -> str:
        """
        Gera chave de cache para os resultados.
        
        Args:
            initial_amount: Valor inicial
            monthly_amount: Valor mensal
            indicators: Lista de indicadores
            indicators_data: Dados dos indicadores
            
        Returns:
            str: Chave de cache
        """
        # Usa hash dos parâmetros para gerar chave única
        params_hash = hash((
            initial_amount,
            monthly_amount,
            tuple(indicators),
            tuple(indicators_data.keys())
        ))
        return f"calculation_{params_hash}"
    
    def _validate_parameters(
        self,
        initial_amount: float,
        monthly_amount: float,
        indicators: List[str],
        indicators_data: Dict
    ) -> None:
        """
        Valida os parâmetros de entrada.
        
        Args:
            initial_amount: Valor inicial
            monthly_amount: Valor mensal
            indicators: Lista de indicadores
            indicators_data: Dados dos indicadores
            
        Raises:
            ValueError: Se os parâmetros forem inválidos
        """
        if initial_amount < 0:
            raise ValueError("Valor inicial deve ser positivo")
        
        if monthly_amount < 0:
            raise ValueError("Valor mensal deve ser positivo")
        
        if not indicators:
            raise ValueError("Pelo menos um indicador deve ser fornecido")
        
        if not indicators_data:
            raise ValueError("Dados dos indicadores não fornecidos")
        
        for indicator in indicators:
            if indicator not in indicators_data:
                raise ValueError(f"Dados do indicador {indicator} não encontrados")
    
    def _calculate_results(
        self,
        initial_amount: float,
        monthly_amount: float,
        indicators: List[str],
        indicators_data: Dict
    ) -> Dict:
        """
        Calcula os resultados da simulação.
        
        Args:
            initial_amount: Valor inicial
            monthly_amount: Valor mensal
            indicators: Lista de indicadores
            indicators_data: Dados dos indicadores
            
        Returns:
            Dict: Resultados do cálculo
        """
        try:
            # Prepara dados
            dates = self._get_dates(indicators_data)
            amounts = self._calculate_amounts(
                initial_amount,
                monthly_amount,
                len(dates)
            )
            
            # Calcula rentabilidade
            returns = self._calculate_returns(indicators, indicators_data)
            total_return = self._calculate_total_return(returns)
            
            # Calcula métricas
            metrics = self._calculate_metrics(amounts, total_return)
            
            # Prepara resultados
            results = {
                'dates': dates,
                'amounts': amounts,
                'returns': returns,
                'total_return': total_return,
                'metrics': metrics
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao calcular resultados: {str(e)}")
            raise
    
    def _get_dates(self, indicators_data: Dict) -> List[datetime]:
        """
        Obtém datas comuns dos indicadores.
        
        Args:
            indicators_data: Dados dos indicadores
            
        Returns:
            List[datetime]: Lista de datas
        """
        dates = set()
        for data in indicators_data.values():
            if isinstance(data, pd.DataFrame):
                dates.update(data.index)
        return sorted(list(dates))
    
    def _calculate_amounts(
        self,
        initial_amount: float,
        monthly_amount: float,
        num_periods: int
    ) -> List[float]:
        """
        Calcula valores acumulados.
        
        Args:
            initial_amount: Valor inicial
            monthly_amount: Valor mensal
            num_periods: Número de períodos
            
        Returns:
            List[float]: Valores acumulados
        """
        amounts = [initial_amount]
        for i in range(1, num_periods):
            amounts.append(amounts[-1] + monthly_amount)
        return amounts
    
    def _calculate_returns(
        self,
        indicators: List[str],
        indicators_data: Dict
    ) -> Dict[str, List[float]]:
        """
        Calcula retornos dos indicadores.
        
        Args:
            indicators: Lista de indicadores
            indicators_data: Dados dos indicadores
            
        Returns:
            Dict[str, List[float]]: Retornos por indicador
        """
        returns = {}
        for indicator in indicators:
            data = indicators_data[indicator]
            if isinstance(data, pd.DataFrame):
                returns[indicator] = data['Close'].pct_change().fillna(0).tolist()
        return returns
    
    def _calculate_total_return(self, returns: Dict[str, List[float]]) -> List[float]:
        """
        Calcula retorno total ponderado.
        
        Args:
            returns: Retornos por indicador
            
        Returns:
            List[float]: Retorno total
        """
        # TODO: Implementar ponderação por indicador
        # Por enquanto usa média simples
        total_return = []
        for i in range(len(next(iter(returns.values())))):
            period_returns = [r[i] for r in returns.values()]
            total_return.append(sum(period_returns) / len(period_returns))
        return total_return
    
    def _calculate_metrics(
        self,
        amounts: List[float],
        total_return: List[float]
    ) -> Dict[str, float]:
        """
        Calcula métricas de performance.
        
        Args:
            amounts: Valores acumulados
            total_return: Retorno total
            
        Returns:
            Dict[str, float]: Métricas calculadas
        """
        # Calcula valor final
        final_amount = amounts[-1] * (1 + sum(total_return))
        
        # Calcula retorno total
        total_return_pct = (final_amount / amounts[0] - 1) * 100
        
        # Calcula retorno médio mensal
        avg_monthly_return = (1 + total_return_pct/100) ** (1/len(total_return)) - 1
        
        # Calcula volatilidade
        volatility = np.std(total_return) * np.sqrt(12) * 100
        
        return {
            'final_amount': final_amount,
            'total_return_pct': total_return_pct,
            'avg_monthly_return': avg_monthly_return,
            'volatility': volatility
        } 