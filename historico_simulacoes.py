import pandas as pd
import json
from datetime import datetime
import os

class HistoricoSimulacoes:
    def __init__(self, arquivo='historico_simulacoes.json'):
        self.arquivo = arquivo
        self.historico = self.carregar_historico()

    def carregar_historico(self):
        """Carrega o histórico de simulações do arquivo."""
        if os.path.exists(self.arquivo):
            try:
                with open(self.arquivo, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def salvar_historico(self):
        """Salva o histórico de simulações no arquivo."""
        with open(self.arquivo, 'w') as f:
            json.dump(self.historico, f, indent=2)

    def adicionar_simulacao(self, dados_simulacao):
        """Adiciona uma nova simulação ao histórico."""
        dados = {
            'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'parametros': {
                'capital_inicial': dados_simulacao['capital_inicial'],
                'retirada_mensal': dados_simulacao['retirada_mensal'],
                'aporte_mensal': dados_simulacao['aporte_mensal'],
                'data_fim': dados_simulacao['data_fim'].strftime('%Y-%m-%d'),
                'reinvestir': dados_simulacao['reinvestir'],
                'taxa_inflacao': dados_simulacao.get('taxa_inflacao', 0),
                'taxa_risco': dados_simulacao.get('taxa_risco', 0)
            },
            'resultados': {
                'capital_final': dados_simulacao['capital_final'],
                'rentabilidade_total': dados_simulacao['rentabilidade_total'],
                'volatilidade': dados_simulacao['volatilidade'],
                'indice_sharpe': dados_simulacao['indice_sharpe']
            },
            'indicadores': dados_simulacao['indicadores']
        }
        self.historico.append(dados)
        self.salvar_historico()

    def obter_historico(self, limite=None):
        """Retorna o histórico de simulações."""
        if limite is not None:
            return self.historico[-limite:]
        return self.historico

    def obter_estatisticas(self):
        """Retorna estatísticas gerais do histórico."""
        if not self.historico:
            return None

        df = pd.DataFrame([
            {
                'Rentabilidade': sim['resultados']['rentabilidade_total'],
                'Volatilidade': sim['resultados']['volatilidade'],
                'Índice Sharpe': sim['resultados']['indice_sharpe'],
                'Capital Final': sim['resultados']['capital_final']
            }
            for sim in self.historico
        ])

        estatisticas = {
            'Total de Simulações': len(self.historico),
            'Média de Rentabilidade': f"{df['Rentabilidade'].mean():.2f}%",
            'Média de Volatilidade': f"{df['Volatilidade'].mean():.2f}%",
            'Média de Índice Sharpe': f"{df['Índice Sharpe'].mean():.2f}",
            'Média de Capital Final': f"{df['Capital Final'].mean():,.2f}"
        }

        return estatisticas

    def comparar_simulacoes(self, sim1, sim2):
        """Compara duas simulações específicas."""
        if sim1 >= len(self.historico) or sim2 >= len(self.historico):
            return None

        s1 = self.historico[sim1]
        s2 = self.historico[sim2]

        comparacao = {
            'Rentabilidade': {
                'Simulação 1': f"{s1['resultados']['rentabilidade_total']:.2f}%",
                'Simulação 2': f"{s2['resultados']['rentabilidade_total']:.2f}%",
                'Diferença': f"{s1['resultados']['rentabilidade_total'] - s2['resultados']['rentabilidade_total']:.2f}%"
            },
            'Volatilidade': {
                'Simulação 1': f"{s1['resultados']['volatilidade']:.2f}%",
                'Simulação 2': f"{s2['resultados']['volatilidade']:.2f}%",
                'Diferença': f"{s1['resultados']['volatilidade'] - s2['resultados']['volatilidade']:.2f}%"
            },
            'Índice Sharpe': {
                'Simulação 1': f"{s1['resultados']['indice_sharpe']:.2f}",
                'Simulação 2': f"{s2['resultados']['indice_sharpe']:.2f}",
                'Diferença': f"{s1['resultados']['indice_sharpe'] - s2['resultados']['indice_sharpe']:.2f}"
            }
        }

        return comparacao
