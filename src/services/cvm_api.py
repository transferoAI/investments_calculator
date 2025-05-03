import pandas as pd
import requests
import zipfile
import io
from datetime import datetime
from typing import Dict, List, Optional

from src.core.types import APIData
from src.core.interfaces import IInvestmentDataFetcher
from src.core.exceptions import APIError

from src.utils.logging import project_logger

class CVMDataFetcher(IInvestmentDataFetcher):
    """Classe para obtenção de dados da CVM."""
    
    def __init__(self):
        """Inicializa o fetcher."""
        self.base_url = "https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS"
        self.logger = project_logger
    
    def fetch_data(self, indicators: List[str], end_date: datetime) -> Dict[str, APIData]:
        """
        Obtém dados dos indicadores da CVM.
        
        Args:
            indicators (List[str]): Lista de CNPJs dos fundos
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
                
                # Limpa o CNPJ para comparação
                cnpj_limpo = indicator.replace('.', '').replace('/', '').replace('-', '')
                
                # Obtém a lista de anos e meses
                date_range = pd.date_range(start_date, end_date, freq='M')
                ano_mes_lista = date_range.strftime('%Y-%m').tolist()
                
                # Coleta os dados
                fund_data = []
                
                for ano_mes in ano_mes_lista:
                    ano, mes = ano_mes.split('-')
                    url = f'{self.base_url}/inf_diario_fi_{ano}{mes}.zip'
                    
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
                                        
                                        fund_data.append({
                                            'mes': f"{ano}-{mes}",
                                            'rentabilidade': rentabilidade
                                        })
                                        
                    except Exception as e:
                        self.logger.error(f"Erro ao processar {ano_mes} para {indicator}: {str(e)}")
                        continue
                
                # Se encontrou dados, cria o DataFrame
                if fund_data:
                    df = pd.DataFrame(fund_data)
                    df['data'] = pd.to_datetime(df['mes'] + '-01')
                    df.set_index('data', inplace=True)
                    df['valor'] = df['rentabilidade']
                    df['index'] = df.index
                    results[indicator] = df
                
            except Exception as e:
                self.logger.error(f"Erro ao obter dados da CVM para {indicator}: {str(e)}")
                raise APIError(f"Erro ao obter dados da CVM para {indicator}")
        
        return results 