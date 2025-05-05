#!/usr/bin/env python3
"""
Script para download e processamento de dados da CVM.
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent))

from src.services.cvm_api import CVMDataFetcher
from src.database.db_manager import DatabaseManager
from constants import FUNDO_CNPJ

def main():
    """Função principal do script."""
    print("Iniciando download dos dados da CVM...")
    
    # Inicializa o downloader
    downloader = CVMDataFetcher()
    
    # Remove o CNPJ do fundo para download
    cnpj = FUNDO_CNPJ.replace(".", "").replace("/", "").replace("-", "")
    
    try:
        # Inicia o download e processamento dos dados
        downloader.download_and_process_fund_data(cnpj)
        print("Download e processamento concluídos com sucesso!")
        
        # Verifica os dados no banco
        db_manager = DatabaseManager()
        fund_data = db_manager.get_fund_data(cnpj)
        if not fund_data.empty:
            print(f"\nDados disponíveis no banco:")
            print(f"- Período: {fund_data['data'].min().strftime('%d/%m/%Y')} a {fund_data['data'].max().strftime('%d/%m/%Y')}")
            print(f"- Total de registros: {len(fund_data)}")
            print(f"- Nome do fundo: {fund_data['nome_fundo'].iloc[0]}")
        else:
            print("\nNenhum dado encontrado no banco.")
            
    except Exception as e:
        print(f"Erro durante o download: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 