import streamlit as st
from datetime import datetime
from typing import Dict
from dateutil.relativedelta import relativedelta

def render_input_form() -> Dict:
    """
    Renderiza o formulário de entrada.
    Esta função renderiza o formulário para entrada dos parâmetros da simulação.
    Returns:
        Dict: Dicionário com os parâmetros inseridos
    """
    try:
        st.header("📝 Parâmetros da Simulação")
        col1, col2 = st.columns(2)
        with col1:
            initial_capital = st.number_input(
                "Capital Inicial (R$)",
                min_value=0.0,
                value=10000.0,
                step=1000.0
            )
            monthly_contribution = st.number_input(
                "Aporte Mensal (R$)",
                min_value=0.0,
                value=1000.0,
                step=100.0
            )
            monthly_withdrawal = st.number_input(
                "Retirada Mensal (R$)",
                min_value=0.0,
                value=0.0,
                step=100.0
            )
        with col2:
            inflation_rate = st.number_input(
                "Taxa de Inflação (% a.a.)",
                min_value=0.0,
                value=5.0,
                step=0.1
            ) / 100
            risk_free_rate = st.number_input(
                "Taxa Livre de Risco (% a.a.)",
                min_value=0.0,
                value=10.0,
                step=0.1
            ) / 100
            months = st.number_input(
                "Período (meses)",
                min_value=1,
                value=12,
                step=1
            )
        start_date = datetime.now()
        end_date = start_date + relativedelta(months=months)
        if st.button("Calcular"):
            return {
                "initial_capital": initial_capital,
                "monthly_contribution": monthly_contribution,
                "monthly_withdrawal": monthly_withdrawal,
                "inflation_rate": inflation_rate,
                "risk_free_rate": risk_free_rate,
                "start_date": start_date,
                "end_date": end_date
            }
        return {}
    except Exception as e:
        st.error(f"Erro ao renderizar formulário: {str(e)}")
        return {} 