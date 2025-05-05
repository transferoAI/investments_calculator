"""
Módulo de gerenciamento do banco de dados.

Este módulo é responsável por:
1. Gerenciar a conexão com o banco DuckDB
2. Definir e criar as tabelas necessárias
3. Fornecer métodos para operações comuns no banco
"""

import duckdb
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
import os
from src.utils.logging import get_logger

class DatabaseManager:
    """Classe para gerenciamento do banco de dados."""
    
    def __init__(self):
        """Inicializa o gerenciador do banco de dados."""
        self.logger = get_logger(__name__)
        self.logger.info("Inicializando DatabaseManager")
        
        # Cria o diretório database se não existir
        os.makedirs("src/database", exist_ok=True)
        
        # Caminho do banco de dados
        self.db_path = "src/database/fundosinvestimento.db"
        self.logger.info(f"Usando banco de dados em: {self.db_path}")
        
        # Inicializa a conexão
        self.conn = duckdb.connect(self.db_path)
        self.logger.info("Conexão com o banco de dados estabelecida")
        
        # Inicializa o banco de dados
        self._init_db()
    
    def _init_db(self):
        """Inicializa o banco de dados e cria as tabelas necessárias."""
        try:
            self.logger.info("Inicializando estrutura do banco de dados")
            # Tabela de cotas dos fundos
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS cotas_fundo (
                    cnpj VARCHAR,
                    nome_fundo VARCHAR,
                    data DATE,
                    vl_quota DECIMAL(15,6),
                    patrimonio_liquido DECIMAL(15,2),
                    captacao DECIMAL(15,2),
                    resgate DECIMAL(15,2),
                    PRIMARY KEY (cnpj, data)
                )
            """)
            self.logger.info("Tabela cotas_fundo criada/verificada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Obtém uma conexão com o banco de dados.
        
        Returns:
            duckdb.DuckDBPyConnection: Conexão com o banco
        """
        return self.conn
    
    def get_last_date_for_fund(self, cnpj: str) -> Optional[datetime]:
        """
        Obtém a última data de dados disponível para um fundo.
        
        Args:
            cnpj (str): CNPJ do fundo
            
        Returns:
            Optional[datetime]: Última data disponível ou None se não houver dados
        """
        try:
            self.logger.info(f"Buscando última data para o fundo {cnpj}")
            result = self._get_connection().execute(f"""
                SELECT MAX(data) as last_date 
                FROM cotas_fundo 
                WHERE cnpj = '{cnpj}'
            """).fetchone()
            last_date = result[0] if result and result[0] else None
            self.logger.info(f"Última data encontrada: {last_date}")
            return last_date
        except Exception as e:
            self.logger.error(f"Erro ao obter última data: {e}")
            return None
    
    def insert_fund_data(self, df: pd.DataFrame):
        """
        Insere dados de um fundo no banco.
        
        Args:
            df (pd.DataFrame): DataFrame com os dados do fundo
        """
        if df.empty:
            self.logger.warning("Tentativa de inserir DataFrame vazio")
            return
            
        try:
            self.logger.info(f"Inserindo {len(df)} registros no banco de dados")
            # Insere os dados, ignorando duplicatas
            self._get_connection().execute("""
                INSERT OR IGNORE INTO cotas_fundo 
                (cnpj, nome_fundo, data, vl_quota, patrimonio_liquido, captacao, resgate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, df.values.tolist())
            self.logger.info("Dados inseridos com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao inserir dados: {e}")
    
    def get_fund_data(
        self,
        cnpj: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Obtém dados de um fundo do banco.
        
        Args:
            cnpj (str): CNPJ do fundo
            start_date (Optional[datetime]): Data inicial
            end_date (Optional[datetime]): Data final
            
        Returns:
            pd.DataFrame: DataFrame com os dados do fundo
        """
        try:
            self.logger.info(f"Buscando dados do fundo {cnpj} entre {start_date} e {end_date}")
            query = f"""
                SELECT * FROM cotas_fundo 
                WHERE cnpj = '{cnpj}'
            """
            
            if start_date:
                query += f" AND data >= '{start_date.strftime('%Y-%m-%d')}'"
            if end_date:
                query += f" AND data <= '{end_date.strftime('%Y-%m-%d')}'"
                
            query += " ORDER BY data"
            
            df = self._get_connection().execute(query).df()
            self.logger.info(f"Encontrados {len(df)} registros")
            return df
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do fundo: {e}")
            return pd.DataFrame()
    
    def get_fund_names(self) -> List[str]:
        """
        Obtém a lista de nomes de fundos no banco.
        
        Returns:
            List[str]: Lista de nomes de fundos
        """
        try:
            self.logger.info("Buscando lista de nomes de fundos")
            result = self._get_connection().execute("""
                SELECT DISTINCT nome_fundo 
                FROM cotas_fundo 
                ORDER BY nome_fundo
            """).fetchall()
            fund_names = [row[0] for row in result]
            self.logger.info(f"Encontrados {len(fund_names)} fundos")
            return fund_names
        except Exception as e:
            self.logger.error(f"Erro ao obter nomes dos fundos: {e}")
            return []
    
    def get_fund_cnpjs(self) -> List[str]:
        """
        Obtém a lista de CNPJs de fundos no banco.
        
        Returns:
            List[str]: Lista de CNPJs
        """
        try:
            self.logger.info("Buscando lista de CNPJs de fundos")
            result = self._get_connection().execute("""
                SELECT DISTINCT cnpj 
                FROM cotas_fundo 
                ORDER BY cnpj
            """).fetchall()
            cnpjs = [row[0] for row in result]
            self.logger.info(f"Encontrados {len(cnpjs)} CNPJs")
            return cnpjs
        except Exception as e:
            self.logger.error(f"Erro ao obter CNPJs dos fundos: {e}")
            return []
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Executa uma query SQL e retorna os resultados como uma lista de dicionários.
        
        Args:
            query (str): Query SQL a ser executada
            
        Returns:
            List[Dict[str, Any]]: Lista de dicionários com os resultados
        """
        try:
            self.logger.info("Executando query personalizada")
            result = self._get_connection().execute(query).fetchall()
            if not result:
                self.logger.info("Query retornou resultados vazios")
                return []
            
            # Converte para lista de dicionários
            columns = [desc[0] for desc in self._get_connection().description]
            data = [dict(zip(columns, row)) for row in result]
            self.logger.info(f"Query retornou {len(data)} registros")
            return data
        except Exception as e:
            self.logger.error(f"Erro ao executar query: {e}")
            return [] 