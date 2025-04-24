import pandas as pd
import requests
import zipfile
import io
import streamlit as st

def obter_rentabilidade_fundo_cvm(cnpj_fundo, ano_mes_lista):
    """
    Obtém a rentabilidade mensal de um fundo de investimento da CVM.
    
    Args:
        cnpj_fundo (str): CNPJ do fundo de investimento
        ano_mes_lista (list): Lista de strings no formato 'YYYY-MM'
        
    Returns:
        list: Lista de dicionários com a rentabilidade mensal
    """
    cnpj_limpo = cnpj_fundo.replace('.', '').replace('/', '').replace('-', '')
    resultados = []
    
    for ano_mes in ano_mes_lista:
        ano, mes = ano_mes.split('-')
        url = f'https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ano}{mes}.zip'
        
        try:
            r = requests.get(url)
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                for file in z.namelist():
                    if file.endswith('.csv'):
                        df = pd.read_csv(z.open(file), sep=';', encoding='latin1', dtype=str)
                        
                        # Verifica se precisa ajustar o cabeçalho
                        if 'CNPJ_FUNDO_CLASSE' not in df.columns:
                            df.columns = df.iloc[0]
                            df = df[1:]
                            
                        # Limpa o CNPJ para comparação
                        df['CNPJ_FUNDO_CLASSE'] = df['CNPJ_FUNDO_CLASSE'].str.replace('.', '').str.replace('/', '').str.replace('-', '')
                        
                        # Filtra pelo CNPJ do fundo
                        df = df[df['CNPJ_FUNDO_CLASSE'] == cnpj_limpo]
                        
                        if not df.empty:
                            # Converte e ordena as datas
                            df['DT_COMPTC'] = pd.to_datetime(df['DT_COMPTC'], errors='coerce')
                            df = df.sort_values('DT_COMPTC')
                            
                            # Converte os valores de quota
                            df['VL_QUOTA'] = pd.to_numeric(df['VL_QUOTA'].str.replace(',', '.'), errors='coerce')
                            
                            # Calcula a rentabilidade
                            inicio = df.iloc[0]['VL_QUOTA']
                            fim = df.iloc[-1]['VL_QUOTA']
                            rentabilidade = ((fim / inicio) - 1) * 100
                            
                            resultados.append({
                                'mes': f"{ano}-{mes}",
                                'rentabilidade': rentabilidade
                            })
                            
        except Exception as e:
            st.warning(f"Erro ao processar {ano_mes}: {e}")
            
    return resultados 