"""
Utilitários para exportação de dados.

Este módulo implementa funções para exportação de resultados
de simulações em diferentes formatos. O módulo é responsável por:

1. Exportar resultados para CSV
2. Exportar resultados para Excel
3. Exportar resultados para JSON
4. Validar dados antes da exportação

IMPORTANTE:
- Validação de dados antes da exportação
- Tratamento adequado de erros
- Formatação consistente dos dados
- Documentação clara dos métodos
"""

import pandas as pd
import xlsxwriter
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, TypedDict, Union, Callable
import io
import base64

from src.core.types import APIData, CalculationOutput
from src.core.interfaces import IExportService
from src.core.exceptions import ExportError

from src.utils.logging import get_logger

# Configuração inicial
logger = get_logger(__name__)

def export_to_excel(df_resultado, indicadores_data, indicadores_selecionados):
    """
    Exporta os resultados para um arquivo Excel.
    
    Args:
        df_resultado (pd.DataFrame): DataFrame com os resultados da simulação
        indicadores_data (dict): Dicionário com os dados dos indicadores
        indicadores_selecionados (list): Lista de indicadores selecionados
        
    Returns:
        bytes: Arquivo Excel em formato binário
    """
    # Criando um buffer para armazenar o arquivo Excel
    output = io.BytesIO()
    
    # Criando um ExcelWriter
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escrevendo o DataFrame de resultados
        df_resultado.to_excel(writer, sheet_name='Resultados', index=False)
        
        # Escrevendo os dados dos indicadores selecionados
        for nome, tipo, codigo in indicadores_selecionados:
            if tipo == 'bcb' and codigo in indicadores_data:
                df = indicadores_data[codigo]
                df.to_excel(writer, sheet_name=nome[:31], index=False)  # Excel limita nomes de planilhas a 31 caracteres
            elif tipo == 'yfinance' and codigo in indicadores_data:
                df = indicadores_data[codigo]
                df.to_excel(writer, sheet_name=nome[:31], index=False)
    
    # Obtendo o conteúdo do buffer
    excel_data = output.getvalue()
    
    return excel_data

def export_to_csv(
    data: CalculationOutput,
    file_path: str,
    include_metadata: bool = True
) -> None:
    """
    Exporta resultados para CSV.
    
    Esta função exporta os resultados de uma simulação
    para um arquivo CSV.
    
    Args:
        data (CalculationOutput): Dados a serem exportados
        file_path (str): Caminho do arquivo de saída
        include_metadata (bool): Incluir metadados no arquivo
        
    Raises:
        ExportError: Se ocorrer erro na exportação
        
    Exemplo:
        export_to_csv(
            data=results,
            file_path="simulacao.csv",
            include_metadata=True
        )
    """
    
    try:
        # Valida os dados
        _validate_export_data(data)
        
        # Cria o diretório se não existir
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepara os dados para exportação
        df = _prepare_data_for_export(data, include_metadata)
        
        # Exporta para CSV
        df.to_csv(output_path, index=False)
        
    except Exception as e:
        raise ExportError(
            f"Erro ao exportar para CSV: {str(e)}",
            {
                "file_path": file_path,
                "include_metadata": include_metadata
            }
        )

def export_to_json(
    data: CalculationOutput,
    file_path: str,
    include_metadata: bool = True
) -> None:
    """
    Exporta resultados para JSON.
    
    Esta função exporta os resultados de uma simulação
    para um arquivo JSON.
    
    Args:
        data (CalculationOutput): Dados a serem exportados
        file_path (str): Caminho do arquivo de saída
        include_metadata (bool): Incluir metadados no arquivo
        
    Raises:
        ExportError: Se ocorrer erro na exportação
        
    Exemplo:
        export_to_json(
            data=results,
            file_path="simulacao.json",
            include_metadata=True
        )
    """
    
    try:
        # Valida os dados
        _validate_export_data(data)
        
        # Cria o diretório se não existir
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepara os dados para exportação
        export_data = _prepare_data_for_json(data, include_metadata)
        
        # Exporta para JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=4, ensure_ascii=False)
        
    except Exception as e:
        raise ExportError(
            f"Erro ao exportar para JSON: {str(e)}",
            {
                "file_path": file_path,
                "include_metadata": include_metadata
            }
        )

def generate_download_link(data, filename, text):
    """
    Gera um link de download para um arquivo.
    
    Args:
        data (bytes or str): Dados do arquivo
        filename (str): Nome do arquivo
        text (str): Texto do link
        
    Returns:
        str: Link de download em formato HTML
    """
    if isinstance(data, bytes):
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{text}</a>'
    else:
        b64 = base64.b64encode(data.encode()).decode()
        href = f'<a href="data:text/csv;base64,{b64}" download="{filename}">{text}</a>'
    
    return href

def generate_report(df_resultado, indicadores_data, indicadores_selecionados):
    """
    Gera um relatório em texto com os resultados da simulação.
    
    Args:
        df_resultado (pd.DataFrame): DataFrame com os resultados da simulação
        indicadores_data (dict): Dicionário com os dados dos indicadores
        indicadores_selecionados (list): Lista de indicadores selecionados
        
    Returns:
        str: Relatório em formato de texto
    """
    # Formatando valores monetários
    def formatar_moeda(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Início do relatório
    report = f"# Relatório de Simulação de Investimentos\n\n"
    report += f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
    
    # Resumo dos resultados
    report += "## Resumo dos Resultados\n\n"
    
    # Capital inicial e final
    capital_inicial = df_resultado.iloc[0]['Capital Final do Mês (BRL)'] - df_resultado.iloc[0]['Rendimento Líquido (BRL)']
    capital_final = df_resultado.iloc[-1]['Capital Final do Mês (BRL)']
    rentabilidade_total = ((capital_final / capital_inicial) - 1) * 100
    
    report += f"- Capital Inicial: {formatar_moeda(capital_inicial)}\n"
    report += f"- Capital Final: {formatar_moeda(capital_final)}\n"
    report += f"- Rentabilidade Total: {rentabilidade_total:.2f}%\n\n"
    
    # Rentabilidade média mensal
    rentabilidade_media = df_resultado['Rentabilidade Líquida (%)'].mean()
    report += f"- Rentabilidade Média Mensal: {rentabilidade_media:.2f}%\n\n"
    
    # Comparação com indicadores
    report += "## Comparação com Indicadores\n\n"
    
    # Obtendo a rentabilidade média de cada indicador
    for nome, tipo, codigo in indicadores_selecionados:
        if tipo == 'bcb' and codigo in indicadores_data:
            df = indicadores_data[codigo]
            if not df.empty:
                rent_media = df['valor'].mean()
                report += f"- {nome}: {rent_media:.2f}% (média mensal)\n"
        elif tipo == 'yfinance' and codigo in indicadores_data:
            df = indicadores_data[codigo]
            if not df.empty:
                rent_media = df['valor'].mean()
                report += f"- {nome}: {rent_media:.2f}% (média mensal)\n"
    
    # Detalhamento mensal
    report += "\n## Detalhamento Mensal\n\n"
    report += "| Mês | Rentabilidade Bruta (%) | CDI (%) | Rentabilidade Líquida (%) | Rendimento Líquido (BRL) | Capital Final (BRL) |\n"
    report += "|-----|------------------------|---------|---------------------------|-------------------------|-------------------|\n"
    
    for _, row in df_resultado.iterrows():
        report += f"| {row['Mês']} | {row['Rentabilidade Bruta (%)']:.2f} | {row['CDI (%)']:.2f} | {row['Rentabilidade Líquida (%)']:.2f} | {formatar_moeda(row['Rendimento Líquido (BRL)'])} | {formatar_moeda(row['Capital Final do Mês (BRL)'])} |\n"
    
    return report

def _validate_export_data(data: CalculationOutput) -> None:
    """
    Valida os dados antes da exportação.
    
    Esta função verifica se os dados estão no formato
    correto e contêm todas as informações necessárias.
    
    Args:
        data (CalculationOutput): Dados a serem validados
        
    Raises:
        ExportError: Se os dados forem inválidos
    """
    
    if not isinstance(data, dict):
        raise ExportError(
            "Dados inválidos para exportação",
            {"data_type": type(data)}
        )
    
    if "results" not in data:
        raise ExportError(
            "Dados não contêm resultados",
            {"data_keys": list(data.keys())}
        )
    
    if "processed_data" not in data:
        raise ExportError(
            "Dados não contêm dados processados",
            {"data_keys": list(data.keys())}
        )

def _prepare_data_for_export(
    data: CalculationOutput,
    include_metadata: bool
) -> pd.DataFrame:
    """
    Prepara os dados para exportação.
    
    Esta função converte os dados para um formato
    adequado para exportação em CSV ou Excel.
    
    Args:
        data (CalculationOutput): Dados a serem preparados
        include_metadata (bool): Incluir metadados
        
    Returns:
        pd.DataFrame: Dados preparados para exportação
    """
    
    # Extrai os resultados
    results = data["results"]
    
    # Cria o DataFrame base
    df = pd.DataFrame({
        "Mês": range(1, len(results["monthly_evolution"]) + 1),
        "Capital": results["monthly_evolution"],
        "Rentabilidade": results["monthly_profitability"]
    })
    
    # Adiciona metadados se necessário
    if include_metadata:
        metadata = _prepare_metadata(data)
        for key, value in metadata.items():
            df[key] = value
    
    return df

def _prepare_data_for_json(
    data: CalculationOutput,
    include_metadata: bool
) -> Dict[str, Any]:
    """
    Prepara os dados para exportação em JSON.
    
    Esta função converte os dados para um formato
    adequado para exportação em JSON.
    
    Args:
        data (CalculationOutput): Dados a serem preparados
        include_metadata (bool): Incluir metadados
        
    Returns:
        Dict[str, Any]: Dados preparados para exportação
    """
    
    # Extrai os resultados
    results = data["results"]
    
    # Prepara os dados básicos
    export_data = {
        "capital_final": results["final_capital"],
        "rentabilidade_total": results["total_profitability"],
        "rentabilidade_anualizada": results["annualized_profitability"],
        "volatilidade": results["volatility"],
        "indice_sharpe": results["sharpe_index"],
        "evolucao_mensal": results["monthly_evolution"],
        "rentabilidade_mensal": results["monthly_profitability"]
    }
    
    # Adiciona metadados se necessário
    if include_metadata:
        export_data["metadados"] = _prepare_metadata(data)
    
    return export_data

def _prepare_metadata(data: CalculationOutput) -> Dict[str, Any]:
    """
    Prepara os metadados para exportação.
    
    Esta função extrai e formata os metadados
    dos resultados da simulação.
    
    Args:
        data (CalculationOutput): Dados contendo os metadados
        
    Returns:
        Dict[str, Any]: Metadados formatados
    """
    
    return {
        "data_exportacao": datetime.now().isoformat(),
        "versao": "1.0.0",
        "formato": "simulacao_investimento"
    } 