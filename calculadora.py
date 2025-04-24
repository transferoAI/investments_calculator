###############################################################################
# Módulo de Cálculo de Rentabilidade
###############################################################################
# Este módulo é responsável por:
# 1. Calcular a rentabilidade de investimentos ao longo do tempo
# 2. Simular cenários com aportes e retiradas
# 3. Integrar dados de diferentes indicadores financeiros
###############################################################################

# Importações necessárias
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta

def calcular_rentabilidade(capital_investido, retirada_mensal, aporte_mensal, data_fim, reinvestir, dados_indicadores):
    """
    Calcula a rentabilidade do investimento com base nos parâmetros fornecidos.
    
    Args:
        capital_investido (float): Capital inicial investido
        retirada_mensal (float): Valor da retirada mensal
        aporte_mensal (float): Valor do aporte mensal
        data_fim (date): Data final da simulação
        reinvestir (bool): Se True, reinveste as retiradas no próximo mês
        dados_indicadores (dict): Dicionário com os dados dos indicadores financeiros
        
    Returns:
        pd.DataFrame: DataFrame com os resultados da simulação contendo:
            - index: Datas mensais da simulação
            - Capital: Saldo inicial de cada mês
            - Retirada: Valor retirado no mês (0 se reinvestir=True)
            - Aporte: Valor aportado no mês
            - Saldo: Saldo final do mês após rentabilidade, retiradas e aportes
            - Rentabilidade: Rentabilidade mensal em percentual
            
    Processo:
        1. Validação e conversão dos valores de entrada
        2. Determinação do período de simulação
        3. Inicialização do DataFrame de resultados
        4. Para cada mês:
           - Calcula rentabilidade média dos indicadores
           - Aplica rentabilidade ao saldo
           - Processa retiradas e aportes
           - Atualiza saldo final
            
    Observações:
        - A rentabilidade é calculada como média dos indicadores disponíveis
        - Suporta indicadores do BCB (valor) e Yahoo Finance (retorno)
        - Trata diferentes formatos de data e fuso horário
        - Em caso de erro nos dados, ignora o indicador problemático
    """
    # Validação e conversão dos valores numéricos
    try:
        capital_investido = float(capital_investido)
        retirada_mensal = float(retirada_mensal)
        aporte_mensal = float(aporte_mensal)
    except (ValueError, TypeError):
        raise ValueError("Os valores de capital, retirada e aporte devem ser números válidos")
    
    # Convertendo a data_fim para datetime se necessário
    if isinstance(data_fim, date):
        data_fim = datetime.combine(data_fim, datetime.min.time())
    
    # Função auxiliar para converter datas para datetime sem fuso horário
    def converter_para_datetime_sem_tz(data):
        if isinstance(data, pd.Timestamp):
            data = data.to_pydatetime()
        if data.tzinfo is not None:
            data = data.replace(tzinfo=None)
        return data
    
    # Determinando a data inicial da simulação
    datas_inicio = []
    for dados in dados_indicadores.values():
        if 'index' in dados and not dados['index'].empty:
            # Convertendo para datetime e removendo informações de fuso horário
            data = dados['index'].iloc[0]
            data = converter_para_datetime_sem_tz(data)
            datas_inicio.append(data)
    
    if not datas_inicio:
        # Se não houver datas de indicadores, usar 5 anos atrás
        data_inicio = data_fim - timedelta(days=5*365)
    else:
        data_inicio = min(datas_inicio)
    
    # Criando o range de datas mensais
    datas = pd.date_range(start=data_inicio, end=data_fim, freq='M')
    
    # Inicializando o DataFrame de resultados
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
        
        # Calculando a rentabilidade média dos indicadores
        rentabilidade = 0.0
        for nome, dados in dados_indicadores.items():
            if 'index' in dados and not dados['index'].empty:
                # Preparando a data atual para comparação
                data_atual = df_resultado.index[i]
                data_atual = converter_para_datetime_sem_tz(data_atual)
                
                # Convertendo datas do DataFrame para datetime sem fuso horário
                dados_sem_tz = dados.copy()
                dados_sem_tz['index'] = dados_sem_tz['index'].apply(converter_para_datetime_sem_tz)
                
                # Encontrando o índice mais próximo da data atual
                indices_proximos = dados_sem_tz[dados_sem_tz['index'] <= data_atual]
                
                if not indices_proximos.empty:
                    idx_mais_proximo = indices_proximos.index[-1]
                    # Processando indicadores do BCB (valor)
                    if 'valor' in dados.columns:
                        try:
                            valor = dados.loc[idx_mais_proximo, 'valor']
                            if isinstance(valor, str):
                                valor = float(valor.replace(',', '.'))
                            rentabilidade += valor / len(dados_indicadores)
                        except (ValueError, TypeError):
                            continue
                    # Processando indicadores do Yahoo Finance (retorno)
                    elif 'retorno' in dados.columns:
                        try:
                            retorno = dados.loc[idx_mais_proximo, 'retorno']
                            if isinstance(retorno, str):
                                retorno = float(retorno.replace(',', '.'))
                            rentabilidade += retorno / len(dados_indicadores)
                        except (ValueError, TypeError):
                            continue
        
        # Atualizando o saldo com a rentabilidade
        saldo_com_rentabilidade = saldo_anterior * (1 + rentabilidade/100)
        
        # Aplicando retirada e aporte conforme a estratégia
        if reinvestir:
            saldo_final = saldo_com_rentabilidade + aporte_mensal
        else:
            saldo_final = saldo_com_rentabilidade - retirada_mensal + aporte_mensal
        
        # Atualizando o DataFrame com os resultados do mês
        df_resultado['Capital'].iloc[i] = saldo_anterior
        df_resultado['Retirada'].iloc[i] = retirada_mensal if not reinvestir else 0
        df_resultado['Aporte'].iloc[i] = aporte_mensal
        df_resultado['Saldo'].iloc[i] = saldo_final
        df_resultado['Rentabilidade'].iloc[i] = rentabilidade
    
    return df_resultado 