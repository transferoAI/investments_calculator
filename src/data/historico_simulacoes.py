import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from src.core.types import (
    SimulationParameters,
    SimulationResults,
    HistoricalSimulation,
    APIData,
    CalculationInput,
    CalculationOutput
)

from src.core.interfaces import ISimulationHistory
from src.core.exceptions import DataNotFoundError

from src.utils.logging import project_logger

class HistoricoSimulacoes(ISimulationHistory):
    """Gerencia o histórico de simulações."""
    
    def __init__(self, arquivo='historico_simulacoes.json'):
        """Inicializa o gerenciador de histórico."""
        self.arquivo = arquivo
        self.historico = self.carregar_historico()

    def carregar_historico(self) -> List[HistoricalSimulation]:
        """Carrega o histórico de simulações do arquivo."""
        if os.path.exists(self.arquivo):
            try:
                with open(self.arquivo, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Erro ao carregar histórico: {str(e)}")
                return []
        return []

    def salvar_historico(self) -> None:
        """Salva o histórico de simulações no arquivo."""
        try:
            with open(self.arquivo, 'w') as f:
                json.dump(self.historico, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico: {str(e)}")

    def add_simulation(self, simulation: HistoricalSimulation) -> None:
        """Adiciona uma nova simulação ao histórico."""
        try:
            self.historico.append(simulation)
            self.salvar_historico()
        except Exception as e:
            self.logger.error(f"Erro ao adicionar simulação: {str(e)}")
            raise DataNotFoundError(f"Erro ao adicionar simulação: {str(e)}")

    def get_history(self, limit: Optional[int] = None) -> List[HistoricalSimulation]:
        """Obtém o histórico de simulações."""
        try:
            if limit is not None:
                return self.historico[-limit:]
            return self.historico
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {str(e)}")
            raise DataNotFoundError(f"Erro ao obter histórico: {str(e)}")

    def get_statistics(self) -> Dict[str, float]:
        """Obtém estatísticas do histórico."""
        try:
            if not self.historico:
                return {}

            df = pd.DataFrame([
                {
                    'Rentabilidade': sim['resultados']['rentabilidade_total'],
                    'Volatilidade': sim['resultados']['volatilidade'],
                    'Índice Sharpe': sim['resultados']['indice_sharpe'],
                    'Capital Final': sim['resultados']['capital_final']
                }
                for sim in self.historico
            ])

            return {
                'Total de Simulações': len(self.historico),
                'Média de Rentabilidade': df['Rentabilidade'].mean(),
                'Média de Volatilidade': df['Volatilidade'].mean(),
                'Média de Índice Sharpe': df['Índice Sharpe'].mean(),
                'Média de Capital Final': df['Capital Final'].mean()
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            raise DataNotFoundError(f"Erro ao obter estatísticas: {str(e)}")
