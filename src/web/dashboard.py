import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Optional
import locale

from src.core.types import (
    SimulationParameters,
    SimulationResults,
    HistoricalSimulation,
    APIData,
    CalculationInput,
    CalculationOutput
)

from src.core.interfaces import ISimulationHistory
from src.core.exceptions import DataNotFoundError

from src.utils.logging import get_logger

# Configurando o locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

# Configuração inicial
logger = get_logger(__name__)

def formatar_moeda(valor):
    """Formata um valor numérico como moeda brasileira (R$)."""
    try:
        return locale.currency(valor, grouping=True, symbol=True)
    except:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_percentual(valor):
    """Formata um valor numérico como percentual."""
    try:
        return f"{valor:.2f}%"
    except:
        return f"{valor}%"

def criar_dashboard():
    """Cria o dashboard com métricas em tempo real."""
    st.markdown("""
        <style>
            .dashboard-section {
                padding: 1.5rem;
                border-radius: var(--border-radius);
                background-color: var(--card-background);
                margin-bottom: 1.5rem;
            }

            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1rem;
                padding: 1rem;
            }

            .metric-card {
                padding: 1rem;
                border-radius: var(--border-radius);
                background-color: rgba(255, 255, 255, 0.1);
                text-align: center;
            }

            .comparison-container {
                display: flex;
                gap: 1rem;
                margin-bottom: 1rem;
            }

            .comparison-select {
                flex: 1;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("📊 Dashboard")

    # Inicializando o histórico
    historico = HistoricoSimulacoes()
    
    # Métricas gerais
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.subheader("📈 Métricas Gerais")
    
    estatisticas = historico.obter_estatisticas()
    if estatisticas:
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
        for metrica, valor in estatisticas.items():
            st.markdown(f'''
                <div class="metric-card">
                    <h4>{metrica}</h4>
                    <p class="metric-value">{valor}</p>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhuma simulação encontrada no histórico.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Últimas simulações
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.subheader("📅 Últimas Simulações")
    
    # Obtendo as últimas 5 simulações
    ultimas_simulacoes = historico.obter_historico(limite=5)
    
    if ultimas_simulacoes:
        # Criando DataFrame com as informações
        df_simulacoes = pd.DataFrame([
            {
                'Data': sim['data'],
                'Rentabilidade': sim['resultados']['rentabilidade_total'],
                'Volatilidade': sim['resultados']['volatilidade'],
                'Índice Sharpe': sim['resultados']['indice_sharpe'],
                'Capital Final': sim['resultados']['capital_final']
            }
            for sim in ultimas_simulacoes
        ])
        
        # Exibindo tabela
        st.dataframe(
            df_simulacoes.style.format({
                'Rentabilidade': formatar_percentual,
                'Volatilidade': formatar_percentual,
                'Índice Sharpe': '{:.2f}',
                'Capital Final': formatar_moeda
            }),
            use_container_width=True
        )
    else:
        st.info("Nenhuma simulação encontrada no histórico.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Análise de performance
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.subheader("📊 Análise de Performance")
    
    # Preparando dados para gráficos
    todas_simulacoes = historico.obter_historico()
    
    if todas_simulacoes:
        # Criando DataFrame com todas as simulações
        df_todas = pd.DataFrame([
            {
                'Data': sim['data'],
                'Rentabilidade': sim['resultados']['rentabilidade_total'],
                'Volatilidade': sim['resultados']['volatilidade'],
                'Índice Sharpe': sim['resultados']['indice_sharpe'],
                'Capital Final': sim['resultados']['capital_final']
            }
            for sim in todas_simulacoes
        ])

        # Gráficos em grid
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de rentabilidade ao longo do tempo
            fig_rentabilidade = px.line(
                df_todas,
                x='Data',
                y='Rentabilidade',
                title='Evolução da Rentabilidade',
                labels={'Rentabilidade': 'Rentabilidade (%)'}
            )
            st.plotly_chart(fig_rentabilidade, use_container_width=True)

            # Gráfico de índice Sharpe
            fig_sharpe = px.box(
                df_todas,
                y='Índice Sharpe',
                title='Distribuição do Índice Sharpe'
            )
            st.plotly_chart(fig_sharpe, use_container_width=True)

        with col2:
            # Gráfico de distribuição de volatilidade
            fig_volatilidade = px.histogram(
                df_todas,
                x='Volatilidade',
                title='Distribuição de Volatilidade',
                labels={'Volatilidade': 'Volatilidade (%)'}
            )
            st.plotly_chart(fig_volatilidade, use_container_width=True)

            # Gráfico de rentabilidade por período
            df_todas['Periodo'] = pd.to_datetime(df_todas['Data']).dt.to_period('M')
            fig_rentabilidade_periodo = px.box(
                df_todas,
                x='Periodo',
                y='Rentabilidade',
                title='Rentabilidade por Período'
            )
            st.plotly_chart(fig_rentabilidade_periodo, use_container_width=True)

    else:
        st.info("Nenhuma simulação encontrada no histórico.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Análise de indicadores
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.subheader("📈 Análise de Indicadores")
    
    # Contagem de uso dos indicadores
    indicadores_usados = {}
    for sim in todas_simulacoes:
        for indicador in sim['indicadores']:
            indicadores_usados[indicador] = indicadores_usados.get(indicador, 0) + 1
    
    if indicadores_usados:
        # Criando DataFrame com os indicadores
        df_indicadores = pd.DataFrame(list(indicadores_usados.items()), columns=['Indicador', 'Contagem'])
        
        # Gráfico de uso dos indicadores
        fig_indicadores = px.bar(
            df_indicadores,
            x='Indicador',
            y='Contagem',
            title='Uso dos Indicadores nas Simulações',
            labels={'Contagem': 'Número de Simulações'}
        )
        st.plotly_chart(fig_indicadores, use_container_width=True)

        # Tabela de indicadores mais usados
        st.subheader("Top Indicadores")
        st.dataframe(
            df_indicadores.sort_values('Contagem', ascending=False).head(5),
            use_container_width=True
        )
    else:
        st.info("Nenhuma simulação encontrada no histórico.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Comparações
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.subheader("🔄 Comparações")
    
    if len(todas_simulacoes) >= 2:
        # Seleção de simulações para comparação
        st.markdown('<div class="comparison-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="comparison-select">', unsafe_allow_html=True)
            sim1 = st.selectbox(
                "Selecione a primeira simulação",
                options=list(range(len(todas_simulacoes))),
                format_func=lambda x: todas_simulacoes[x]['data']
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="comparison-select">', unsafe_allow_html=True)
            sim2 = st.selectbox(
                "Selecione a segunda simulação",
                options=list(range(len(todas_simulacoes))),
                format_func=lambda x: todas_simulacoes[x]['data']
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Comparar Simulações"):
            comparacao = historico.comparar_simulacoes(sim1, sim2)
            if comparacao:
                st.subheader("📊 Resultado da Comparação")
                for metrica, valores in comparacao.items():
                    st.metric(
                        metrica,
                        valores['Diferença'],
                        delta=valores['Diferença']
                    )
    else:
        st.info("É necessário ter pelo menos duas simulações para fazer comparações.")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    criar_dashboard()
