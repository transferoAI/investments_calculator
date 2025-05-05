"""
Módulo da página de simulação.

Este módulo contém a lógica e interface da página de simulação de investimentos.
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Tuple

from src.core.types import APIData, SimulationParameters, SimulationResults
from src.core.exceptions import APIError, CalculationError
from src.core.investment_calculator import calcular_rentabilidade

from src.web.components.input_form import render_input_form
from src.web.components.indicator_selector import render_indicator_selector
from src.web.components.results import render_results
from src.web.components.formatters import format_currency, format_percentage

def render_simulation_page():
    """Renderiza a página de simulação."""
    st.header("Simulação de Investimentos")
    
    # Renderiza o formulário de entrada
    resultado_form = render_input_form()
    
    if resultado_form:
        # Desempacota os valores do formulário
        data_inicio_analise, data_fim, capital_investido, retirada_mensal, aporte_mensal, reinvestir = resultado_form
        
        # Seleção de indicadores para comparação
        indicadores_selecionados, calcular = render_indicator_selector()
        
        # Processamento dos cálculos quando o botão é pressionado
        if calcular:
            try:
                # Inicialização da barra de progresso
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Obtém dados dos indicadores
                status_text.text("Obtendo dados dos indicadores...")
                progress_bar.progress(20)
                
                # Cálculo da rentabilidade
                status_text.text("Calculando rentabilidade...")
                progress_bar.progress(60)
                
                try:
                    df_resultado = calcular_rentabilidade(
                        capital_investido=capital_investido,
                        retirada_mensal=retirada_mensal,
                        aporte_mensal=aporte_mensal,
                        data_fim=data_fim,
                        reinvestir=reinvestir,
                        dados_indicadores={}  # TODO: Implementar obtenção de dados
                    )
                except CalculationError as e:
                    st.error(f"Erro ao calcular rentabilidade: {str(e)}")
                    st.stop()
                
                # Exibição dos resultados
                status_text.text("Finalizando...")
                progress_bar.progress(100)
                
                # Renderiza os resultados
                render_results(df_resultado, {}, indicadores_selecionados)
                
            except APIError as e:
                st.error(f"Erro ao obter dados: {str(e)}")
            except Exception as e:
                st.error(f"Erro inesperado: {str(e)}")
    else:
        st.info("Preencha os campos acima e clique em 'Calcular Rentabilidade' para ver os resultados.") 