from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from src.core.types import (
    SimulationParameters,
    SimulationResults,
    HistoricalSimulation,
    APIData,
    CalculationInput,
    CalculationOutput
)

from src.core.interfaces import IInvestmentCalculator
from src.core.exceptions import CalculationError

from src.services.bcb_api import BCBDataFetcher
from src.services.cvm_api import CVMDataFetcher
from src.services.yfinance_api import YFinanceDataFetcher
from src.utils.logging import project_logger

class InvestmentCalculator(IInvestmentCalculator):
    """Classe principal para cálculo de investimentos."""
    
    def __init__(self):
        """Inicializa o calculador."""
        self.bcb_fetcher = BCBDataFetcher()
        self.cvm_fetcher = CVMDataFetcher()
        self.yfinance_fetcher = YFinanceDataFetcher()
        self.logger = project_logger
    
    def calculate(self, input_data: CalculationInput) -> CalculationOutput:
        """
        Calcula a rentabilidade do investimento.
        
        Args:
            input_data (CalculationInput): Dados de entrada para o cálculo
            
        Returns:
            CalculationOutput: Resultados do cálculo
        
        Raises:
            CalculationError: Se ocorrer erro no cálculo
        """
        try:
            # Obtendo dados dos indicadores
            dados_indicadores = {}
            
            for indicador in input_data['indicadores_selecionados']:
                tipo, codigo = indicador
                if tipo == 'bcb':
                    dados = self.bcb_fetcher.fetch_data(codigo, input_data['data_fim'])
                elif tipo == 'cvm':
                    dados = self.cvm_fetcher.fetch_data(codigo, input_data['data_fim'])
                elif tipo == 'yfinance':
                    dados = self.yfinance_fetcher.fetch_data(codigo, input_data['data_fim'])
                
                if dados is not None:
                    dados_indicadores[codigo] = dados
            
            # Calculando a rentabilidade
            df_resultado = calcular_rentabilidade(
                input_data['capital_investido'],
                input_data['retirada_mensal'],
                input_data['aporte_mensal'],
                input_data['data_fim'],
                input_data['reinvestir'],
                dados_indicadores
            )
            
            # Calculando métricas adicionais
            rentabilidade_total = ((df_resultado['Saldo'].iloc[-1] / input_data['capital_investido']) - 1) * 100
            volatilidade = df_resultado['Rentabilidade'].std()
            indice_sharpe = rentabilidade_total / volatilidade if volatilidade != 0 else 0
            
            # Criando o resultado
            resultados = {
                'capital_final': df_resultado['Saldo'].iloc[-1],
                'rentabilidade_total': rentabilidade_total,
                'volatilidade': volatilidade,
                'indice_sharpe': indice_sharpe
            }
            
            return {
                'df_resultado': df_resultado,
                'indicadores_selecionados': input_data['indicadores_selecionados'],
                'mostrar_tendencias': input_data['mostrar_tendencias'],
                'mostrar_estatisticas': input_data['mostrar_estatisticas']
            }
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo: {str(e)}")
            raise CalculationError(str(e))
    # Garantindo que os valores numéricos sejam do tipo float
    try:
        capital_investido = float(capital_investido)
        retirada_mensal = float(retirada_mensal)
        aporte_mensal = float(aporte_mensal)
    except (ValueError, TypeError):
        raise ValueError("Os valores de capital, retirada e aporte devem ser números válidos")
    
    # Criando o DataFrame de resultados
    # Convertendo a data_fim para datetime se for date
    if isinstance(data_fim, date):
        data_fim = datetime.combine(data_fim, datetime.min.time())
    
    # Função auxiliar para converter datas para datetime sem fuso horário
    def converter_para_datetime_sem_tz(data):
        if isinstance(data, pd.Timestamp):
            data = data.to_pydatetime()
        if data.tzinfo is not None:
            data = data.replace(tzinfo=None)
        return data
    
    # Encontrando a data inicial como o mínimo entre as datas dos indicadores
    datas_inicio = []
    for dados in dados_indicadores.values():
        if 'index' in dados and not dados['index'].empty:
            # Convertendo para datetime se necessário e removendo informações de fuso horário
            data = dados['index'].iloc[0]
            data = converter_para_datetime_sem_tz(data)
            datas_inicio.append(data)
    
    if not datas_inicio:
        # Se não houver datas de indicadores, usar 5 anos atrás
        data_inicio = data_fim - timedelta(days=5*365)
    else:
        data_inicio = min(datas_inicio)
    
    # Criando o range de datas
    datas = pd.date_range(start=data_inicio, end=data_fim, freq='M')
    
    df_resultado = pd.DataFrame(index=datas)
    df_resultado['Capital'] = capital_investido
    df_resultado['Retirada'] = retirada_mensal
    df_resultado['Aporte'] = aporte_mensal
    df_resultado['Saldo'] = capital_investido
    df_resultado['Rentabilidade'] = 0.0
    
    # Calculando a rentabilidade mês a mês
    for i in range(1, len(df_resultado)):
        # Obtendo o saldo do mês anterior
        saldo_anterior = df_resultado['Saldo'].iloc[i-1]
        
        # Calculando a rentabilidade do mês
        rentabilidade = 0.0
        for nome, dados in dados_indicadores.items():
            if 'index' in dados and not dados['index'].empty:
                # Encontrando o índice mais próximo da data atual
                data_atual = df_resultado.index[i]
                data_atual = converter_para_datetime_sem_tz(data_atual)
                
                # Convertendo todas as datas do DataFrame para datetime sem fuso horário
                dados_sem_tz = dados.copy()
                dados_sem_tz['index'] = dados_sem_tz['index'].apply(converter_para_datetime_sem_tz)
                
                # Encontrando o índice mais próximo da data atual
                indices_proximos = dados_sem_tz[dados_sem_tz['index'] <= data_atual]
                
                if not indices_proximos.empty:
                    idx_mais_proximo = indices_proximos.index[-1]
                    if 'valor' in dados.columns:
                        try:
                            valor = dados.loc[idx_mais_proximo, 'valor']
                            # Garantindo que o valor seja numérico
                            if isinstance(valor, str):
                                valor = float(valor.replace(',', '.'))
                            rentabilidade += valor / len(dados_indicadores)
                        except (ValueError, TypeError):
                            # Se não conseguir converter, ignora este indicador
                            continue
                    elif 'retorno' in dados.columns:
                        try:
                            retorno = dados.loc[idx_mais_proximo, 'retorno']
                            # Garantindo que o retorno seja numérico
                            if isinstance(retorno, str):
                                retorno = float(retorno.replace(',', '.'))
                            rentabilidade += retorno / len(dados_indicadores)
                        except (ValueError, TypeError):
                            # Se não conseguir converter, ignora este indicador
                            continue
        
        # Atualizando o saldo com a rentabilidade
        saldo_com_rentabilidade = saldo_anterior * (1 + rentabilidade/100)
        
        # Aplicando retirada e aporte
        if reinvestir:
            saldo_final = saldo_com_rentabilidade + aporte_mensal
        else:
            saldo_final = saldo_com_rentabilidade - retirada_mensal + aporte_mensal
        
        # Atualizando o DataFrame
        df_resultado['Capital'].iloc[i] = saldo_anterior
        df_resultado['Retirada'].iloc[i] = retirada_mensal if not reinvestir else 0
        df_resultado['Aporte'].iloc[i] = aporte_mensal
        df_resultado['Saldo'].iloc[i] = saldo_final
        df_resultado['Rentabilidade'].iloc[i] = rentabilidade
    
    return df_resultado 