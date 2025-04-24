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
    # Inicializando o tema na sessão se não existir
    if 'theme' not in st.session_state:
        st.session_state.theme = "High Contrast"  # Definindo High Contrast como padrão
    
    with st.sidebar:
        st.title("Configurações")
        # Usando session_state para manter o tema selecionado
        selected_theme = st.selectbox(
            "Tema",
            options=["High Contrast", "Light", "Dark", "Blue", "Green"],  # High Contrast como primeira opção
            index=["High Contrast", "Light", "Dark", "Blue", "Green"].index(st.session_state.theme),
            key="theme_selector"
        )
        # Atualizando o tema na sessão
        st.session_state.theme = selected_theme
    
    return selected_theme

def apply_theme(theme):
    """Aplica o tema selecionado."""
    # Garantindo que o tema seja uma string válida
    theme = str(theme).strip()
    if theme not in ["Light", "Dark", "Blue", "Green", "High Contrast"]:
        theme = "Light"  # Tema padrão se receber um valor inválido
        
    theme_configs = {
        "Light": {
            "background": "#FFFFFF",
            "text": "#262730",
            "primary": "#FF4B4B",
            "secondary": "#0068C9",
            "accent": "#83C9FF",
            "sidebar": "#F0F2F6",
            "plot_background": "#FFFFFF",
            "plot_text": "#262730",
            "plot_grid": "#E5E5E5"
        },
        "Dark": {
            "background": "#0E1117",
            "text": "#FAFAFA",
            "primary": "#FF4B4B",
            "secondary": "#00C0F2",
            "accent": "#00B4EB",
            "sidebar": "#262730",
            "plot_background": "#1E1E1E",
            "plot_text": "#FAFAFA",
            "plot_grid": "#333333"
        },
        "Blue": {
            "background": "#EFF6FF",
            "text": "#1E293B",
            "primary": "#3B82F6",
            "secondary": "#1D4ED8",
            "accent": "#60A5FA",
            "sidebar": "#DBEAFE",
            "plot_background": "#EFF6FF",
            "plot_text": "#1E293B",
            "plot_grid": "#BFDBFE"
        },
        "Green": {
            "background": "#F0FDF4",
            "text": "#14532D",
            "primary": "#22C55E",
            "secondary": "#15803D",
            "accent": "#4ADE80",
            "sidebar": "#DCFCE7",
            "plot_background": "#F0FDF4",
            "plot_text": "#14532D",
            "plot_grid": "#BBF7D0"
        },
        "High Contrast": {
            "background": "#000000",
            "text": "#FFFFFF",
            "primary": "#FFFF00",
            "secondary": "#00FF00",
            "accent": "#FF00FF",
            "sidebar": "#1A1A1A",
            "plot_background": "#000000",
            "plot_text": "#FFFFFF",
            "plot_grid": "#333333"
        }
    }
    
    colors = theme_configs[theme]
    
    css = f"""
        <style>
            /* Main app */
            .stApp {{
                background-color: {colors["background"]};
                color: {colors["text"]};
            }}
            
            /* Sidebar */
            section[data-testid="stSidebar"] {{
                background-color: {colors["sidebar"]};
            }}
            
            /* Buttons */
            .stButton>button {{
                background-color: {colors["primary"]};
                color: {colors["background"]};
                border: none;
                border-radius: 4px;
                padding: 0.5rem 1rem;
                transition: all 0.2s;
            }}
            .stButton>button:hover {{
                background-color: {colors["secondary"]};
                transform: translateY(-2px);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            
            /* Input fields */
            .stTextInput>div>div>input,
            .stNumberInput>div>div>input,
            .stDateInput>div>div>input {{
                background-color: {colors["background"]};
                color: {colors["text"]};
                border: 1px solid {colors["accent"]};
                border-radius: 4px;
            }}
            
            /* Selectbox */
            .stSelectbox>div>div {{
                background-color: {colors["background"]};
                color: {colors["text"]};
                border: 1px solid {colors["accent"]};
                border-radius: 4px;
            }}
            
            /* Multiselect */
            .stMultiSelect>div>div {{
                background-color: {colors["background"]};
                color: {colors["text"]};
                border: 1px solid {colors["accent"]};
                border-radius: 4px;
            }}
            
            /* Checkbox */
            .stCheckbox>div {{
                background-color: {colors["background"]};
                color: {colors["text"]};
            }}
            
            /* Progress bar */
            .stProgress>div>div>div>div {{
                background-color: {colors["primary"]};
            }}
            
            /* Plots */
            .js-plotly-plot {{
                background-color: {colors["plot_background"]};
            }}
            .js-plotly-plot .plotly .main-svg {{
                background-color: {colors["plot_background"]} !important;
            }}
            
            /* DataFrames */
            .dataframe {{
                background-color: {colors["background"]};
                color: {colors["text"]};
            }}
            .dataframe th {{
                background-color: {colors["accent"]};
                color: {colors["text"]};
            }}
            
            /* Metrics */
            [data-testid="stMetricValue"] {{
                color: {colors["primary"]};
                font-weight: bold;
            }}
            
            /* Headers */
            h1, h2, h3, h4, h5, h6 {{
                color: {colors["text"]};
            }}
            
            /* Links */
            a {{
                color: {colors["primary"]};
                text-decoration: none;
            }}
            a:hover {{
                color: {colors["secondary"]};
                text-decoration: underline;
            }}
            
            /* Tooltips */
            .stTooltipIcon {{
                color: {colors["accent"]};
            }}
        </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    
    # Configurando o estilo dos gráficos matplotlib com parâmetros válidos
    plt.style.use('default')
    plt.rcParams.update({
        'figure.facecolor': colors["plot_background"],
        'axes.facecolor': colors["plot_background"],
        'axes.edgecolor': colors["plot_text"],
        'axes.labelcolor': colors["plot_text"],
        'axes.grid': True,
        'grid.color': colors["plot_grid"],
        'grid.alpha': 0.3,
        'text.color': colors["plot_text"],
        'xtick.color': colors["plot_text"],
        'ytick.color': colors["plot_text"],
        'figure.dpi': 100
    })

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