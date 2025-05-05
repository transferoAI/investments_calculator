import pandas as pd
import requests
import zipfile
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, TypedDict, Union, Any, Callable
import os
from constants import FUNDO_CNPJ
from src.core.types import APIData
from src.core.interfaces import IInvestmentDataFetcher
from src.core.exceptions import APIError

from src.utils.logging import get_logger

class CVMDataFetcher(IInvestmentDataFetcher):
    """Classe para obtenção de dados da CVM."""
    
    def __init__(self):
        """Inicializa o fetcher."""
        self.base_url = "https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS"
        self.logger = get_logger(__name__)
        self.logger.info("Inicializando CVMDataFetcher")
        
        # Estrutura de diretórios
        self.data_dir = "data/cvm"
        self.zip_dir = os.path.join(self.data_dir, "zip")
        self.csv_dir = os.path.join(self.data_dir, "csv")
        self.pending_dir = os.path.join(self.csv_dir, "pendentes")
        self.processed_dir = os.path.join(self.csv_dir, "processados")
        
        # Cria os diretórios necessários
        for dir_path in [self.zip_dir, self.pending_dir, self.processed_dir]:
            os.makedirs(dir_path, exist_ok=True)
            self.logger.info(f"Criado diretório: {dir_path}")
            
        # Status do download
        self.status = {
            "is_running": False,
            "status": "",
            "progress": 0,
            "processed_months": 0,
            "total_months": 0
        }
        
        # Inicializa o gerenciador do banco de dados
        try:
            self.logger.info("Inicializando DatabaseManager")
            from src.database.db_manager import DatabaseManager
            self.db_manager = DatabaseManager()
            self.logger.info("DatabaseManager inicializado com sucesso")
            self.logger.info(f"db_manager type: {type(self.db_manager)}")
            self.logger.info(f"db_manager attributes: {dir(self.db_manager)}")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar DatabaseManager: {e}")
            raise
    
    def _clean_cnpj(self, cnpj: str) -> str:
        """
        Remove a formatação do CNPJ.
        
        Args:
            cnpj (str): CNPJ com ou sem formatação
            
        Returns:
            str: CNPJ sem formatação
        """
        return cnpj.replace(".", "").replace("/", "").replace("-", "")
    
    def _get_file_paths(self, year_month: str) -> tuple:
        """
        Retorna os caminhos dos arquivos para um determinado mês/ano.
        
        Args:
            year_month (str): Ano e mês no formato YYYYMM
            
        Returns:
            tuple: (caminho_zip, caminho_csv_pendente, caminho_csv_processado)
        """
        base_name = f"inf_diario_fi_{year_month}"
        return (
            os.path.join(self.zip_dir, f"{base_name}.zip"),
            os.path.join(self.pending_dir, f"{base_name}.csv"),
            os.path.join(self.processed_dir, f"{base_name}.csv")
        )
    
    def _extract_csv(self, zip_path: str, csv_path: str) -> bool:
        """
        Extrai o arquivo CSV do ZIP.
        
        Args:
            zip_path (str): Caminho do arquivo ZIP
            csv_path (str): Caminho de destino do CSV
            
        Returns:
            bool: True se a extração foi bem sucedida
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                csv_file = zip_ref.namelist()[0]
                with zip_ref.open(csv_file) as source, open(csv_path, 'wb') as target:
                    target.write(source.read())
            return True
        except Exception as e:
            self.logger.error(f"Erro ao extrair {zip_path}: {str(e)}")
            return False
    
    def _check_fund_in_file(self, file_path: str, cnpj: str) -> bool:
        """
        Verifica rapidamente se um fundo existe no arquivo CSV.
        
        Args:
            file_path (str): Caminho do arquivo CSV
            cnpj (str): CNPJ do fundo no formato original (com formatação)
            
        Returns:
            bool: True se o fundo existe no arquivo
        """
        try:
            self.logger.info(f"Verificando CNPJ {cnpj} no arquivo {file_path}")
            
            # Usa grep para verificar rapidamente se o CNPJ existe no arquivo
            with open(file_path, 'r', encoding='latin1') as f:
                for line in f:
                    if cnpj in line:
                        self.logger.info(f"CNPJ {cnpj} encontrado no arquivo")
                        return True
            self.logger.info(f"CNPJ {cnpj} não encontrado no arquivo")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar fundo no arquivo {file_path}: {str(e)}")
            return False

    def _process_csv_file(self, file_path: str, cnpj: str) -> Optional[pd.DataFrame]:
        """
        Processa um arquivo CSV e retorna os dados do fundo.
        
        Args:
            file_path (str): Caminho do arquivo CSV
            cnpj (str): CNPJ do fundo no formato original (com formatação)
            
        Returns:
            Optional[pd.DataFrame]: DataFrame com os dados do fundo ou None se não houver dados
        """
        try:
            self.logger.info(f"Processando arquivo {file_path} para CNPJ {cnpj}")
                        
            # Verifica se o arquivo contém o fundo antes de processar
            if not self._check_fund_in_file(file_path, cnpj):
                self.logger.warning(f"Fundo {cnpj} não encontrado no arquivo {file_path}")
                return None
                
            # Verifica o formato do arquivo
            try:
                with open(file_path, 'r', encoding='latin1') as f:
                    first_line = f.readline()
                    if 'CNPJ_FUNDO' not in first_line:
                        self.logger.error(f"Arquivo {file_path} não contém a coluna CNPJ_FUNDO")
                        return None
                    self.logger.info(f"Cabeçalho do arquivo: {first_line.strip()}")
            except Exception as e:
                self.logger.error(f"Erro ao verificar arquivo CSV: {str(e)}")
                return None
                
            # Lê apenas as linhas do fundo específico
            cnpj_clean = self._clean_cnpj(cnpj)
            self.logger.info(f"CNPJ formatado: {cnpj}, CNPJ limpo: {cnpj_clean}")
            
            query = f"""
            SELECT * FROM read_csv('{file_path}', 
                delim=';',
                header=True,
                encoding='latin-1',
                auto_detect=false,
                strict_mode=false,
                quote='"',
                escape='"',
                ignore_errors=true,
                null_padding=true,
                max_line_size=10000000,
                columns={{
                    'CNPJ_FUNDO': 'VARCHAR',
                    'DENOM_SOCIAL': 'VARCHAR',
                    'DT_COMPTC': 'DATE',
                    'VL_QUOTA': 'DOUBLE',
                    'VL_PATRIM_LIQ': 'DOUBLE',
                    'CAPTC_DIA': 'DOUBLE',
                    'RESG_DIA': 'DOUBLE'
                }}
            )
            WHERE CNPJ_FUNDO = '{cnpj_clean}'
            """
            
            self.logger.info(f"Query: {query}")
            
            try:
                data = self.db_manager.execute_query(query)
                if data:
                    df = pd.DataFrame(data)
                    self.logger.info(f"DataFrame criado com sucesso. Colunas: {df.columns.tolist()}")
                    self.logger.info(f"Primeiras linhas do DataFrame:\n{df.head()}")
                    self.logger.info(f"Tipos de dados:\n{df.dtypes}")
                    
                    # Converte a coluna de data
                    df['DT_COMPTC'] = pd.to_datetime(df['DT_COMPTC'])
                    self.logger.info(f"Arquivo processado com sucesso. Encontrados {len(df)} registros.")
                    return df
                self.logger.warning("Nenhum dado retornado pela query")
                return None
            except Exception as e:
                self.logger.error(f"Erro ao executar query no DuckDB: {str(e)}")
                self.logger.error(f"Tipo do erro: {type(e).__name__}")
                self.logger.error(f"Detalhes do erro: {str(e)}")
                return None
            
        except Exception as e:
            self.logger.error(f"Erro ao processar arquivo CSV {file_path}: {str(e)}")
            self.logger.error(f"Tipo do erro: {type(e).__name__}")
            self.logger.error(f"Detalhes do erro: {str(e)}")
            return None

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
        
        # Verifica se db_manager está disponível
        if not hasattr(self, 'db_manager'):
            self.logger.error("db_manager não está disponível")
            raise APIError("Erro de inicialização: db_manager não está disponível")
        
        self.logger.info(f"Iniciando busca de dados para {len(indicators)} fundos")
        self.logger.info(f"Data final: {end_date}")
        
        for cnpj in indicators:
            try:
                # Remove formatação do CNPJ para a API
                cnpj_clean = self._clean_cnpj(cnpj)
                self.logger.info(f"Processando fundo: CNPJ formatado={cnpj}, CNPJ limpo={cnpj_clean}")
                
                # Calculando a data inicial (5 anos atrás)
                start_date = end_date - timedelta(days=365)
                self.logger.info(f"Período de busca: {start_date.date()} até {end_date.date()}")
                
                # Lista para armazenar os dados de todos os anos
                all_data = []
                
                # Inicializa o status
                self.status["is_running"] = True
                self.status["status"] = "Iniciando download..."
                self.status["progress"] = 0
                self.status["processed_months"] = 0
                
                # Calcula o total de meses a processar
                total_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
                self.status["total_months"] = total_months
                self.logger.info(f"Total de meses a processar: {total_months}")
                
                # Itera sobre os anos necessários
                for year in range(start_date.year, end_date.year + 1):
                    for month in range(1, 13):
                        # Pula meses futuros
                        if year == end_date.year and month > end_date.month:
                            continue
                            
                        try:
                            # Obtendo os dados da CVM
                            year_month = f"{year}{month:02d}"
                            url = f"{self.base_url}/inf_diario_fi_{year_month}.zip"
                            self.logger.info(f"Processando mês {year_month}")
                            
                            # Obtém os caminhos dos arquivos
                            zip_path, pending_path, processed_path = self._get_file_paths(year_month)
                            self.logger.info(f"Arquivos: ZIP={zip_path}, Pending={pending_path}, Processed={processed_path}")
                            
                            # Verifica se já temos o arquivo processado
                            if os.path.exists(processed_path):
                                self.logger.info(f"Arquivo processado encontrado: {processed_path}")
                                # Verifica se o arquivo contém dados do fundo
                                df = self._process_csv_file(processed_path, cnpj)  # Usa CNPJ formatado
                                if df is not None and not df.empty:
                                    self.logger.info(f"Arquivo {processed_path} já processado e contém dados do fundo {cnpj}")
                                    all_data.append(df)
                                    self.status["processed_months"] += 1
                                    self.status["progress"] = int((self.status["processed_months"] / total_months) * 100)
                                    self.status["status"] = f"Processando... {self.status['processed_months']}/{total_months} meses"
                                    continue
                                else:
                                    self.logger.warning(f"Arquivo {processed_path} não contém dados do fundo {cnpj} ou ocorreu um erro no processamento")
                            
                            # Verifica se é o mês atual
                            is_current_month = (year == end_date.year and month == end_date.month)
                            self.logger.info(f"É mês atual? {is_current_month}")
                            
                            # Só baixa o ZIP se for o mês atual ou se não temos o arquivo
                            if is_current_month or not os.path.exists(zip_path):
                                self.logger.info(f"Baixando dados de {year_month} de {url}")
                                response = requests.get(url)
                                response.raise_for_status()
                                
                                # Salva o arquivo ZIP
                                with open(zip_path, 'wb') as f:
                                    f.write(response.content)
                                self.logger.info(f"Arquivo ZIP salvo em {zip_path}")
                            else:
                                self.logger.info(f"Arquivo ZIP já existe: {zip_path}")
                            
                            # Extrai o CSV se não existir ou se for o mês atual
                            if not os.path.exists(pending_path) or is_current_month:
                                self.logger.info(f"Extraindo CSV para {pending_path}")
                                if not self._extract_csv(zip_path, pending_path):
                                    self.logger.error(f"Erro ao extrair arquivo {zip_path}")
                                    continue
                            else:
                                self.logger.info(f"Arquivo CSV já existe: {pending_path}")
                            
                            # Lê e processa o arquivo CSV local
                            df = self._process_csv_file(pending_path, FUNDO_CNPJ)
                            
                            if df is not None and not df.empty:
                                self.logger.info(f"Encontrados {len(df)} registros para o fundo {cnpj}")
                                # Move o arquivo para processados
                                if os.path.exists(pending_path):
                                    os.rename(pending_path, processed_path)
                                    self.logger.info(f"Arquivo movido para {processed_path}")
                                all_data.append(df)
                                self.status["processed_months"] += 1
                                self.status["progress"] = int((self.status["processed_months"] / total_months) * 100)
                                self.status["status"] = f"Processando... {self.status['processed_months']}/{total_months} meses"
                            else:                                
                                self.logger.warning(f"Nenhum dado encontrado para o fundo {FUNDO_CNPJ} no arquivo {pending_path}")
                                    
                        except requests.exceptions.RequestException as e:
                            self.logger.error(f"Erro ao baixar dados de {year_month}: {str(e)}")
                            continue
                        except Exception as e:
                            self.logger.error(f"Erro ao processar dados de {year_month}: {str(e)}")
                            self.logger.error(f"Tipo do erro: {type(e).__name__}")
                            self.logger.error(f"Detalhes do erro: {str(e)}")
                            continue
                    
                if all_data:
                    # Concatena todos os dados
                    data = pd.concat(all_data, ignore_index=True)
                    self.logger.info(f"Total de registros concatenados: {len(data)}")
                    
                    # Converte a coluna de data
                    data['DT_COMPTC'] = pd.to_datetime(data['DT_COMPTC'])
                    
                    # Filtra pelo período desejado
                    data = data[(data['DT_COMPTC'] >= start_date) & (data['DT_COMPTC'] <= end_date)]
                    self.logger.info(f"Registros após filtro de data: {len(data)}")
                    
                    if not data.empty:
                        # Ordena por data
                        data = data.sort_values('DT_COMPTC')
                        
                        # Calcula o retorno diário
                        data['retorno'] = data['VL_QUOTA'].pct_change() * 100
                        
                        # Remove a primeira linha (NaN)
                        data = data.dropna()
                        self.logger.info(f"Registros após remoção de NaN: {len(data)}")
                        
                        # Adiciona a coluna de índice
                        data['index'] = data['DT_COMPTC']
                        
                        # Salva os dados usando o CNPJ sem formatação como chave
                        results[cnpj_clean] = data
                        self.logger.info(f"Dados processados com sucesso para {cnpj_clean}")
                    else:
                        self.logger.warning(f"Nenhum dado encontrado para o período especificado")
                else:
                    self.logger.warning(f"Nenhum dado encontrado para o CNPJ {cnpj_clean}")
                
                # Atualiza o status final
                self.status["status"] = f"Download concluído! {self.status['processed_months']} meses processados"
                self.status["is_running"] = False
                
            except Exception as e:
                self.logger.error(f"Erro ao obter dados da CVM para {cnpj_clean}: {str(e)}")
                self.logger.error(f"Tipo do erro: {type(e).__name__}")
                self.logger.error(f"Detalhes do erro: {str(e)}")
                self.status["status"] = f"Erro: {str(e)}"
                self.status["is_running"] = False
                raise APIError(
                    f"Erro ao obter dados da CVM para {cnpj_clean}",
                    {"cnpj": cnpj_clean, "error": str(e)}
                )
        
        return results

    def get_status(self) -> Dict:
        """
        Retorna o status atual do download.
        
        Returns:
            Dict: Status do download
        """
        return self.status 