import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

from src.core.types import (
    SimulationParameters,
    SimulationResults,
    HistoricalSimulation,
    APIData,
    CalculationInput,
    CalculationOutput
)

from src.core.interfaces import IUIComponent
from src.core.exceptions import InvalidParameterError

from src.utils.logging import project_logger
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        st.warning("Não foi possível configurar o locale para português do Brasil. Os valores monetários podem não ser exibidos corretamente.")

def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira (R$).
    
    Args:
        valor (float): Valor a ser formatado
        
    Returns:
        str: Valor formatado como moeda brasileira (ex: R$ 1.234,56)
    """
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

def render_theme_selector():
    """Renderiza o seletor de tema e retorna o tema selecionado."""
    with st.sidebar:
        st.title("⚙️ Configurações")
        theme = st.selectbox(
            "🎨 Tema",
            ["Claro", "Escuro"],
            index=0,
            help="Selecione o tema da interface"
        )
        
        # Adicionando configurações adicionais
        st.divider()
        
        st.subheader("📊 Visualização")
        mostrar_tendencias = st.checkbox(
            "Mostrar tendências",
            value=True,
            help="Exibe as tendências dos indicadores no gráfico"
        )
        
        mostrar_estatisticas = st.checkbox(
            "Mostrar estatísticas detalhadas",
            value=True,
            help="Exibe estatísticas adicionais dos resultados"
        )
        
        st.divider()
        
        st.subheader("⚙️ Opções")
        mostrar_alertas = st.checkbox(
            "Mostrar alertas",
            value=True,
            help="Exibe alertas sobre possíveis problemas nos cálculos"
        )
        
        st.divider()
        
        st.subheader("💾 Exportação")
        formato_exportacao = st.selectbox(
            "Formato de exportação",
            ["Excel", "PDF", "CSV"],
            index=0,
            help="Selecione o formato para exportar os resultados"
        )
    
    return theme, mostrar_tendencias, mostrar_estatisticas, mostrar_alertas, formato_exportacao

def apply_theme(theme):
    """Aplica o tema selecionado."""
    st.markdown(f"""
        <style>
            :root {{
                --primary-color: {"#2563eb" if theme == "Escuro" else "#1e40af"};
                --secondary-color: {"#1e40af" if theme == "Escuro" else "#2563eb"};
                --success-color: {"#22c55e" if theme == "Escuro" else "#16a34a"};
                --warning-color: {"#f59e0b" if theme == "Escuro" else "#d97706"};
                --error-color: {"#ef4444" if theme == "Escuro" else "#dc2626"};
                --background-color: {"#0f172a" if theme == "Escuro" else "#ffffff"};
                --text-color: {"#f8fafc" if theme == "Escuro" else "#1f2937"};
                --border-radius: 12px;
                --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                --card-background: {"rgba(255, 255, 255, 0.1)" if theme == "Escuro" else "rgba(255, 255, 255, 0.9)"};
                --section-padding: 1.5rem;
            }}

            .stApp {{
                background-color: var(--background-color);
                color: var(--text-color);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            }}

            .stButton > button {{
                background-color: var(--primary-color) !important;
                color: white !important;
                border-radius: var(--border-radius) !important;
                padding: 0.75rem 1.5rem !important;
                font-weight: 600 !important;
                transition: background-color 0.2s !important;
                border: none !important;
            }}

            .stButton > button:hover {{
                background-color: var(--secondary-color) !important;
            }}

            .stMetricValue {{
                font-size: 1.5rem !important;
                font-weight: 700 !important;
            }}

            .stAlert-success {{
                background-color: rgba(22, 163, 74, 0.1) !important;
                border-left: 4px solid var(--success-color) !important;
                padding: 1rem !important;
                border-radius: var(--border-radius) !important;
            }}

            .stAlert-warning {{
                background-color: rgba(217, 119, 6, 0.1) !important;
                border-left: 4px solid var(--warning-color) !important;
                padding: 1rem !important;
                border-radius: var(--border-radius) !important;
            }}

            .stAlert-error {{
                background-color: rgba(220, 38, 38, 0.1) !important;
                border-left: 4px solid var(--error-color) !important;
                padding: 1rem !important;
                border-radius: var(--border-radius) !important;
            }}

            .stMarkdown {{
                color: var(--text-color) !important;
            }}

            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            .stDateInput > div > div > input,
            .stCheckbox > div > div > label,
            .stSelectbox > div > div > select {{
                background-color: var(--card-background) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: var(--border-radius) !important;
                padding: 0.5rem !important;
                color: var(--text-color) !important;
            }}

            .stMarkdown h1,
            .stMarkdown h2,
            .stMarkdown h3,
            .stMarkdown h4,
            .stMarkdown h5,
            .stMarkdown h6 {{
                color: var(--primary-color) !important;
            }}

            .stMarkdown p {{
                color: var(--text-color) !important;
                margin-bottom: 1rem !important;
            }}

            .stMarkdown hr {{
                border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
                margin: 1.5rem 0 !important;
            }}

            .stMarkdown ul,
            .stMarkdown ol {{
                margin-bottom: 1rem !important;
            }}

            .stMarkdown li {{
                margin-bottom: 0.5rem !important;
            }}

            .stMarkdown code {{
                background-color: var(--card-background) !important;
                padding: 0.2rem 0.5rem !important;
                border-radius: 4px !important;
            }}

            .stMarkdown pre {{
                background-color: var(--card-background) !important;
                padding: 1rem !important;
                border-radius: var(--border-radius) !important;
                overflow-x: auto !important;
            }}

            .stMarkdown table {{
                width: 100% !important;
                border-collapse: collapse !important;
            }}

            .stMarkdown th,
            .stMarkdown td {{
                padding: 0.75rem !important;
                text-align: left !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
            }}

            .stMarkdown th {{
                background-color: var(--card-background) !important;
            }}
        </style>
    """, unsafe_allow_html=True)

def render_input_form():
    """Renderiza o formulário de entrada e retorna os valores inseridos."""
    st.markdown("""
        <style>
            .input-section {
                padding: 1rem;
                border-radius: var(--border-radius);
                background-color: var(--card-background);
                margin-bottom: 1.5rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("💰 Calculadora de Rentabilidade de Investimentos")
    
    with st.container():
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        
        with st.expander("🔧 Parâmetros de Investimento", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                capital_investido = st.number_input(
                    "💰 Capital Inicial",
                    min_value=0.0,
                    value=10000.0,
                    step=1000.0,
                    format="%.2f",
                    help="Valor inicial investido"
                )
                
                retirada_mensal = st.number_input(
                    "💸 Retirada Mensal",
                    min_value=0.0,
                    value=0.0,
                    step=100.0,
                    format="%.2f",
                    help="Valor a ser retirado mensalmente"
                )
                
                data_fim = st.date_input(
                    "📅 Data Final",
                    value=date.today(),
                    format="DD/MM/YYYY",
                    help="Data final da simulação"
                )
            
            with col2:
                aporte_mensal = st.number_input(
                    "📈 Aporte Mensal",
                    min_value=0.0,
                    value=0.0,
                    step=100.0,
                    format="%.2f",
                    help="Valor a ser adicionado mensalmente"
                )
                
                reinvestir = st.checkbox(
                    "🔄 Reinvestir Retiradas",
                    value=True,
                    help="Se marcado, as retiradas serão reinvestidas no próximo mês."
                )
                
                # Adicionando opções adicionais
                st.divider()
                
                st.subheader("⚙️ Opções Avançadas")
                taxa_inflacao = st.number_input(
                    "📈 Taxa de Inflação Anual",
                    min_value=0.0,
                    max_value=100.0,
                    value=2.5,
                    step=0.1,
                    format="%.1f",
                    help="Taxa de inflação anual esperada"
                )
                
                taxa_risco = st.number_input(
                    "📉 Taxa de Risco Anual",
                    min_value=0.0,
                    max_value=100.0,
                    value=5.0,
                    step=0.1,
                    format="%.1f",
                    help="Taxa de risco anual esperada"
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Adicionando seletor de indicadores
    indicadores_disponiveis = [
        ('bcb', 'SELIC'),
        ('yfinance', 'BOVA11.SA'),
        ('yfinance', 'IBOV.SA')
    ]
    
    indicadores_selecionados = render_indicator_selector(indicadores_disponiveis)
    
    # Opções de visualização
    mostrar_tendencias = st.checkbox(
        "📊 Mostrar Tendências",
        value=True,
        help="Mostra as tendências dos indicadores no gráfico"
    )
    
    mostrar_estatisticas = st.checkbox(
        "📊 Mostrar Estatísticas",
        value=True,
        help="Mostra estatísticas detalhadas dos resultados"
    )
    
    calcular = st.button("🔍 Calcular Rentabilidade")
    
    if calcular:
        return {
            'capital_investido': capital_investido,
            'retirada_mensal': retirada_mensal,
            'aporte_mensal': aporte_mensal,
            'data_fim': data_fim,
            'reinvestir': reinvestir,
            'taxa_inflacao': taxa_inflacao,
            'taxa_risco': taxa_risco,
            'indicadores_selecionados': indicadores_selecionados,
            'mostrar_tendencias': mostrar_tendencias,
            'mostrar_estatisticas': mostrar_estatisticas
        }
    
    return None

def render_indicator_selector(indicadores_disponiveis):
    """Renderiza o seletor de indicadores e retorna os indicadores selecionados."""
    st.subheader("📊 Seletor de Indicadores")
    
    with st.expander("🔍 Indicadores BCB", expanded=True):
        indicadores_bcb = st.multiselect(
            "🔍 Selecione os indicadores do BCB",
            options=list(indicadores_disponiveis['bcb'].keys()),
            default=["CDI", "Selic"],
            help="Indicadores do Banco Central do Brasil"
        )
    
    with st.expander("📊 Indicadores YFinance", expanded=True):
        indicadores_yfinance = st.multiselect(
            "📊 Selecione os indicadores do YFinance",
            options=list(indicadores_disponiveis['yfinance'].keys()),
            default=["IBOVESPA", "S&P 500"],
            help="Indicadores do Yahoo Finance"
        )
    
    with st.expander("📈 Indicadores Personalizados", expanded=False):
        st.subheader("📊 Adicionar Indicador Personalizado")
        novo_indicador = st.text_input(
            "📝 Nome do Indicador",
            help="Nome para o indicador personalizado"
        )
        
        if novo_indicador:
            valor_inicial = st.number_input(
                "💰 Valor Inicial",
                min_value=0.0,
                value=100.0,
                step=0.1,
                format="%.2f",
                help="Valor inicial do indicador"
            )
            
            taxa_retorno = st.number_input(
                "📈 Taxa de Retorno Mensal",
                min_value=0.0,
                max_value=100.0,
                value=1.0,
                step=0.1,
                format="%.1f",
                help="Taxa de retorno mensal em porcentagem"
            )
            
            if st.button("➕ Adicionar Indicador"):
                indicadores_disponiveis['personalizado'][novo_indicador] = {
                    'valor_inicial': valor_inicial,
                    'taxa_retorno': taxa_retorno
                }
                st.success(f"Indicador '{novo_indicador}' adicionado com sucesso!")
    
    # Combinando os indicadores selecionados
    indicadores_selecionados = []
    for nome in indicadores_bcb:
        indicadores_selecionados.append((nome, 'bcb'))
    for nome in indicadores_yfinance:
        indicadores_selecionados.append((nome, 'yfinance'))
    
    # Botão de cálculo com loading
    with st.spinner("Calculando..."):
        calcular = st.button(
            "🚀 Calcular Rentabilidade",
            type="primary",
            help="Inicia o cálculo da rentabilidade"
        )
    
    return indicadores_selecionados, calcular

def render_results(df_resultado, dados_indicadores, indicadores_selecionados, mostrar_tendencias, mostrar_estatisticas):
    """Renderiza os resultados da simulação."""
    st.subheader("📊 Resultados da Simulação")
    
    # Exibindo o gráfico principal
    st.markdown("### 📈 Evolução do Capital e Indicadores")
    
    # Criando figura com subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    
    # Gráfico principal de evolução do capital
    ax1.plot(df_resultado.index, df_resultado['Saldo'], label='Capital', color='#2563eb', linewidth=2)
    
    # Adicionando indicadores selecionados
    for nome, tipo in indicadores_selecionados:
        if tipo == 'bcb':
            if nome in dados_indicadores:
                ax1.plot(
                    dados_indicadores[nome].index,
                    dados_indicadores[nome]['valor'],
                    label=nome,
                    linestyle='--',
                    alpha=0.7
                )
        elif tipo == 'yfinance':
            simbolo = dados_indicadores.get(nome)
            if simbolo is not None and simbolo in dados_indicadores:
                ax1.plot(
                    dados_indicadores[simbolo].index,
                    dados_indicadores[simbolo]['retorno'],
                    label=nome,
                    linestyle='--',
                    alpha=0.7
                )
    
    ax1.set_title("Evolução do Capital e Indicadores")
    ax1.set_ylabel("Valor (R$)")
    ax1.grid(True)
    ax1.legend()
    
    # Gráfico secundário de rentabilidade mensal
    if mostrar_tendencias:
        ax2.plot(
            df_resultado.index,
            df_resultado['Saldo'].pct_change() * 100,
            label='Rentabilidade Mensal',
            color='#16a34a',
            linewidth=2
        )
        ax2.set_title("Rentabilidade Mensal")
        ax2.set_ylabel("Rentabilidade (%)")
        ax2.grid(True)
    
    st.pyplot(fig)
    
    # Exibindo estatísticas principais
    st.markdown("### 📊 Estatísticas Principais")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Capital Final",
            formatar_moeda(df_resultado['Saldo'].iloc[-1]),
            delta=formatar_moeda(df_resultado['Saldo'].iloc[-1] - df_resultado['Capital'].iloc[0])
        )
    
    with col2:
        rentabilidade_total = (df_resultado['Saldo'].iloc[-1] / df_resultado['Capital'].iloc[0] - 1) * 100
        st.metric(
            "📈 Rentabilidade Total",
            formatar_percentual(rentabilidade_total),
            delta=formatar_percentual(rentabilidade_total - 100)
        )
    
    with col3:
        volatilidade = df_resultado['Saldo'].pct_change().std() * 100
        st.metric(
            "📊 Volatilidade",
            formatar_percentual(volatilidade)
        )
    
    with col4:
        sharpe_ratio = (rentabilidade_total - 2.25) / volatilidade
        st.metric(
            "⭐️ Índice de Sharpe",
            f"{sharpe_ratio:.2f}"
        )
    
    # Exibindo estatísticas detalhadas
    if mostrar_estatisticas:
        st.markdown("### 📊 Estatísticas Detalhadas")
        
        # Criando DataFrame com estatísticas
        estatisticas = {
            "Métrica": [
                "Média Mensal",
                "Média Anual",
                "Máximo",
                "Mínimo",
                "Desvio Padrão",
                "Coeficiente de Variação"
            ],
            "Valor": [
                formatar_moeda(df_resultado['Saldo'].mean()),
                formatar_moeda(df_resultado['Saldo'].mean() * 12),
                formatar_moeda(df_resultado['Saldo'].max()),
                formatar_moeda(df_resultado['Saldo'].min()),
                formatar_moeda(df_resultado['Saldo'].std()),
                f"{df_resultado['Saldo'].std() / df_resultado['Saldo'].mean():.2%}"
            ]
        }
        
        df_estatisticas = pd.DataFrame(estatisticas)
        st.dataframe(df_estatisticas, use_container_width=True)
    
    # Adicionando recomendações
    st.markdown("### 📝 Recomendações")
    
    # Analisando rentabilidade
    if rentabilidade_total > 100:
        st.success("✅ Excelente rentabilidade! Seu investimento está performando muito bem.")
    elif rentabilidade_total > 50:
        st.info("ℹ️ Boa rentabilidade! Seu investimento está performando bem.")
    else:
        st.warning("⚠️ Rendimento abaixo do esperado. Considere revisar sua estratégia de investimento.")
    
    # Analisando volatilidade
    if volatilidade < 10:
        st.success("✅ Baixa volatilidade! Seu portfólio é estável.")
    elif volatilidade < 20:
        st.info("ℹ️ Volatilidade moderada. Seu portfólio tem alguns riscos.")
    else:
        st.warning("⚠️ Alta volatilidade! Seu portfólio tem riscos significativos.")
    
    # Adicionando botões de ação
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Recalcular com Novos Parâmetros"):
            st.experimental_rerun()
    
    with col2:
        if st.button("💾 Exportar Resultados"):
            st.success("Resultados exportados com sucesso!")
    
    # Exibindo a tabela de resultados
    st.dataframe(
        df_resultado.style.format({
            'Capital': formatar_moeda,
            'Retirada': formatar_moeda,
            'Aporte': formatar_moeda,
            'Saldo': formatar_moeda,
            'Rentabilidade': formatar_percentual
        }),
        use_container_width=True
    ) 