import pandas as pd
import xlsxwriter
from datetime import datetime
from typing import Dict, List, Optional

from src.core.types import APIData
from src.core.interfaces import IExportService
from src.core.exceptions import ExportError

from src.utils.logging import project_logger

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

def export_to_csv(df_resultado):
    """
    Exporta os resultados para um arquivo CSV.
    
    Args:
        df_resultado (pd.DataFrame): DataFrame com os resultados da simulação
        
    Returns:
        str: Conteúdo do arquivo CSV
    """
    return df_resultado.to_csv(index=False)

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