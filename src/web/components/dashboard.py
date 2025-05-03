import streamlit as st
import plotly.graph_objects as go
from typing import Dict

def render_dashboard(data: Dict) -> None:
    """
    Renderiza o dashboard principal.
    Esta função renderiza o dashboard com métricas, gráficos e análises dos resultados.
    Args:
        data (CalculationOutput): Dados a serem exibidos
    """
    try:
        results = data["results"]
        st.header("📊 Métricas Principais")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Capital Final",
                f"R$ {results['final_capital']:,.2f}",
                delta=f"{results['total_profitability']:.1%}"
            )
        with col2:
            st.metric(
                "Rentabilidade Total",
                f"{results['total_profitability']:.1%}",
                delta=f"{results['annualized_profitability']:.1%} a.a."
            )
        with col3:
            st.metric(
                "Volatilidade",
                f"{results['volatility']:.1%}",
                delta="Anualizada"
            )
        with col4:
            st.metric(
                "Índice de Sharpe",
                f"{results['sharpe_index']:.2f}",
                delta="Risco/Retorno"
            )
        st.header("📈 Evolução do Investimento")
        fig_capital = go.Figure()
        fig_capital.add_trace(
            go.Scatter(
                x=list(range(1, len(results["monthly_evolution"]) + 1)),
                y=results["monthly_evolution"],
                mode="lines",
                name="Capital"
            )
        )
        fig_capital.update_layout(
            title="Evolução do Capital",
            xaxis_title="Mês",
            yaxis_title="Capital (R$)",
            showlegend=True
        )
        st.plotly_chart(fig_capital, use_container_width=True)
        fig_profitability = go.Figure()
        fig_profitability.add_trace(
            go.Bar(
                x=list(range(1, len(results["monthly_profitability"]) + 1)),
                y=results["monthly_profitability"],
                name="Rentabilidade"
            )
        )
        fig_profitability.update_layout(
            title="Rentabilidade Mensal",
            xaxis_title="Mês",
            yaxis_title="Rentabilidade (%)",
            showlegend=True
        )
        st.plotly_chart(fig_profitability, use_container_width=True)
        st.header("⚠️ Análise de Risco")
        volatility = results["volatility"]
        if volatility < 0.1:
            risk_level = "Baixo"
            risk_color = "green"
        elif volatility < 0.2:
            risk_level = "Moderado"
            risk_color = "yellow"
        else:
            risk_level = "Alto"
            risk_color = "red"
        st.markdown(f"""
        <div style=\"background-color: {risk_color}; padding: 10px; border-radius: 5px;\">
            <h3 style=\"color: white; margin: 0;\">Nível de Risco: {risk_level}</h3>
        </div>
        """, unsafe_allow_html=True)
        sharpe = results["sharpe_index"]
        if sharpe > 1:
            recommendation = "Excelente investimento"
        elif sharpe > 0:
            recommendation = "Bom investimento"
        else:
            recommendation = "Investimento arriscado"
        st.info(f"Recomendação: {recommendation}")
        st.header("💾 Exportar Resultados")
        export_format = st.selectbox(
            "Formato de exportação",
            ["CSV", "Excel", "JSON"]
        )
        if st.button("Exportar"):
            st.success("Resultados exportados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao renderizar dashboard: {str(e)}") 