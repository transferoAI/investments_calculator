###############################################################################
# API de Integração com a CVM (Comissão de Valores Mobiliários)
###############################################################################
# Este módulo é responsável por:
# 1. Obter dados de fundos de investimento da CVM
# 2. Processar arquivos CSV com informações diárias dos fundos
# 3. Calcular rentabilidade mensal dos fundos
###############################################################################

# Importações necessárias
import pandas as pd
import requests
import zipfile
import io
import streamlit as st
from datetime import datetime, timedelta, date
from constants import FUNDO_CNPJ

def obter_data_inicio_fundo():
    """
    Obtém a data de início do fundo na CVM.
    
    Returns:
        datetime: Data de início do fundo (julho de 2024)
        
    Observações:
        - Esta função retorna uma data fixa que representa o início das operações
          do fundo na CVM
        - Atualmente está configurada para julho de 2024
    """
    # Data de início conhecida do fundo
    return datetime(2024, 7, 1)

def obter_rentabilidade_fundo_cvm(data_inicio, data_fim):
    """
    Obtém a rentabilidade mensal do fundo de investimento da CVM.
    
    Args:
        data_inicio (date): Data inicial da análise
        data_fim (date): Data final da análise
        
    Returns:
        list: Lista de dicionários com a rentabilidade mensal, onde cada dicionário
             contém:
             - 'mes': string no formato 'YYYY-MM'
             - 'rentabilidade': float representando a rentabilidade em percentual
             
    Processo:
        1. Verifica e ajusta a data inicial se necessário
        2. Limpa o CNPJ do fundo removendo caracteres especiais
        3. Gera uma lista de períodos mensais entre as datas
        4. Para cada mês:
           - Baixa o arquivo ZIP da CVM
           - Extrai e processa o arquivo CSV
           - Filtra os dados pelo CNPJ do fundo
           - Calcula a rentabilidade mensal
           
    Observações:
        - Os arquivos da CVM são baixados do endereço:
          https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/
        - O cálculo da rentabilidade é feito usando o valor da primeira e última
          quota do mês
        - Erros no processamento de um mês específico são registrados como warnings
          no Streamlit
    """
    # Garantir que a data inicial não seja anterior a julho de 2024
    data_inicio_fundo = datetime(2024, 7, 1).date()
    if data_inicio < data_inicio_fundo:
        data_inicio = data_inicio_fundo
        st.warning("A data inicial foi ajustada para julho de 2024, que é a data de início do fundo.")
    
    # Limpeza do CNPJ para comparação com os dados da CVM
    cnpj_limpo = FUNDO_CNPJ.replace('.', '').replace('/', '').replace('-', '')
    
    # Gera lista de ano_mes entre data_inicio e data_fim
    ano_mes_lista = []
    data_atual = data_inicio
    while data_atual <= data_fim:
        ano_mes_lista.append(data_atual.strftime('%Y-%m'))
        # Avança para o próximo mês
        if data_atual.month == 12:
            data_atual = date(data_atual.year + 1, 1, 1)
        else:
            data_atual = date(data_atual.year, data_atual.month + 1, 1)
    
    # Lista para armazenar os resultados de rentabilidade
    resultados = []
    
    # Processa cada mês individualmente
    for ano_mes in ano_mes_lista:
        ano, mes = ano_mes.split('-')
        url = f'https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ano}{mes}.zip'
        
        try:
            # Download e extração do arquivo ZIP
            r = requests.get(url)
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                for file in z.namelist():
                    if file.endswith('.csv'):
                        # Lê o arquivo CSV
                        df = pd.read_csv(z.open(file), sep=';', encoding='latin1', dtype=str)
                        
                        # Verifica se precisa ajustar o cabeçalho
                        if 'CNPJ_FUNDO_CLASSE' not in df.columns:
                            df.columns = df.iloc[0]
                            df = df[1:]
                            
                        # Limpa o CNPJ para comparação
                        df['CNPJ_FUNDO_CLASSE'] = df['CNPJ_FUNDO_CLASSE'].str.replace('.', '').str.replace('/', '').str.replace('-', '')
                        
                        # Filtra pelo CNPJ do fundo
                        df_filtrado = df[df['CNPJ_FUNDO_CLASSE'] == cnpj_limpo]
                        
                        if not df_filtrado.empty:
                            # Converte e ordena as datas
                            df_filtrado['DT_COMPTC'] = pd.to_datetime(df_filtrado['DT_COMPTC'], errors='coerce')
                            df_filtrado = df_filtrado.sort_values('DT_COMPTC')
                            
                            # Converte os valores de quota
                            df_filtrado['VL_QUOTA'] = pd.to_numeric(df_filtrado['VL_QUOTA'].str.replace(',', '.'), errors='coerce')
                            
                            # Calcula a rentabilidade do mês
                            inicio = df_filtrado.iloc[0]['VL_QUOTA']
                            fim = df_filtrado.iloc[-1]['VL_QUOTA']
                            rentabilidade = ((fim / inicio) - 1) * 100
                            
                            # Adiciona o resultado à lista
                            resultados.append({
                                'mes': f"{ano}-{mes}",
                                'rentabilidade': rentabilidade
                            })
                            
        except Exception as e:
            st.warning(f"Erro ao processar {ano_mes}: {e}")
            
    return resultados 