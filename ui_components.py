import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
# Removendo a importação do seaborn que não está sendo usado
# import seaborn as sns
import locale
from datetime import date, datetime

# Configurando o locale para português do Brasil
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
        st.title("Configurações")
        theme = st.selectbox(
            "Tema",
            ["light", "dark"],
            index=0
        )
    return theme

def apply_theme(theme):
    """Aplica o tema selecionado."""
    if theme == "dark":
        st.markdown("""
            <style>
                .stApp {
                    background-color: #0E1117;
                    color: #FAFAFA;
                }
                .stButton>button {
                    background-color: #262730;
                    color: #FAFAFA;
                }
                .stSelectbox>div>div {
                    background-color: #262730;
                    color: #FAFAFA;
                }
                .stTextInput>div>div>input {
                    background-color: #262730;
                    color: #FAFAFA;
                }
                .stDateInput>div>div>input {
                    background-color: #262730;
                    color: #FAFAFA;
                }
                .stCheckbox>div {
                    background-color: #262730;
                    color: #FAFAFA;
                }
            </style>
        """, unsafe_allow_html=True)

def render_input_form():
    """Renderiza o formulário de entrada e retorna os valores inseridos."""
    st.title("Calculadora de Rentabilidade de Investimentos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        capital_investido = st.number_input(
            "Capital Inicial (R$)",
            min_value=0.0,
            value=10000.0,
            step=1000.0,
            format="%.2f"
        )
        
        retirada_mensal = st.number_input(
            "Retirada Mensal (R$)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f"
        )
        
        data_fim = st.date_input(
            "Data Final",
            value=date.today(),
            format="DD/MM/YYYY"
        )
    
    with col2:
        aporte_mensal = st.number_input(
            "Aporte Mensal (R$)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f"
        )
        
        reinvestir = st.checkbox(
            "Reinvestir Retiradas",
            value=True,
            help="Se marcado, as retiradas serão reinvestidas no próximo mês."
        )
    
    return capital_investido, retirada_mensal, aporte_mensal, data_fim, reinvestir

def render_indicator_selector(indicadores_disponiveis):
    """Renderiza o seletor de indicadores e retorna os indicadores selecionados."""
    st.subheader("Indicadores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        indicadores_bcb = st.multiselect(
            "Indicadores BCB",
            options=list(indicadores_disponiveis['bcb'].keys()),
            default=["CDI", "Selic"],
            help="Selecione os indicadores do Banco Central do Brasil."
        )
    
    with col2:
        indicadores_yfinance = st.multiselect(
            "Indicadores YFinance",
            options=list(indicadores_disponiveis['yfinance'].keys()),
            default=["IBOVESPA", "S&P 500"],
            help="Selecione os indicadores do Yahoo Finance."
        )
    
    # Combinando os indicadores selecionados
    indicadores_selecionados = []
    for nome in indicadores_bcb:
        indicadores_selecionados.append((nome, 'bcb'))
    for nome in indicadores_yfinance:
        indicadores_selecionados.append((nome, 'yfinance'))
    
    # Botão de cálculo
    calcular = st.button("Calcular Rentabilidade", type="primary")
    
    return indicadores_selecionados, calcular

def render_results(df_resultado, dados_indicadores, indicadores_selecionados):
    """Renderiza os resultados da simulação."""
    st.subheader("Resultados")
    
    # Exibindo o gráfico de evolução do capital
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_resultado.index, df_resultado['Saldo'], label='Capital', linewidth=2)
    
    # Adicionando os indicadores selecionados ao gráfico
    for nome, tipo in indicadores_selecionados:
        if tipo == 'bcb':
            if nome in dados_indicadores:
                ax.plot(dados_indicadores[nome].index, dados_indicadores[nome]['valor'], label=nome, linestyle='--')
        elif tipo == 'yfinance':
            simbolo = dados_indicadores.get(nome)
            if simbolo is not None and simbolo in dados_indicadores:
                ax.plot(dados_indicadores[simbolo].index, dados_indicadores[simbolo]['retorno'], label=nome, linestyle='--')
    
    ax.set_title("Evolução do Capital e Indicadores")
    ax.set_xlabel("Data")
    ax.set_ylabel("Valor")
    ax.grid(True)
    ax.legend()
    
    st.pyplot(fig)
    
    # Exibindo estatísticas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Capital Final",
            formatar_moeda(df_resultado['Saldo'].iloc[-1])
        )
    
    with col2:
        rentabilidade_total = (df_resultado['Saldo'].iloc[-1] / df_resultado['Capital'].iloc[0] - 1) * 100
        st.metric(
            "Rentabilidade Total",
            formatar_percentual(rentabilidade_total)
        )
    
    with col3:
        rentabilidade_media = df_resultado['Rentabilidade'].mean()
        st.metric(
            "Rentabilidade Média Mensal",
            formatar_percentual(rentabilidade_media)
        )
    
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