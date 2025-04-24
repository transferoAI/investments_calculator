import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
# Removendo a importação do seaborn que não está sendo usado
# import seaborn as sns
import locale
from datetime import date, datetime
from cvm_api import obter_data_inicio_fundo

# Configurando o locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        st.warning("Não foi possível configurar o locale para português do Brasil. Os valores monetários podem não ser exibidos corretamente.")

def formatar_moeda(valor, currency="BRL"):
    """
    Formata um valor numérico como moeda (R$ ou US$).
    
    Args:
        valor (float): Valor a ser formatado
        currency (str): Código da moeda (BRL ou USD)
        
    Returns:
        str: Valor formatado como moeda
    """
    if currency == "BRL":
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            return locale.currency(valor, grouping=True, symbol=True)
        except:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:  # USD
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            return locale.currency(valor, grouping=True, symbol=True)
        except:
            return f"$ {valor:,.2f}"

def formatar_percentual(valor):
    """Formata um valor numérico como percentual."""
    try:
        return f"{valor:.2f}%"
    except:
        return f"{valor}%"

def render_theme_selector():
    """Renderiza o seletor de tema, idioma e moeda e retorna as configurações."""
    # Inicializando as configurações na sessão se não existirem
    if 'theme' not in st.session_state:
        st.session_state.theme = "High Contrast"
    if 'language' not in st.session_state:
        st.session_state.language = "Português"
    if 'currency' not in st.session_state:
        st.session_state.currency = "BRL"
    
    with st.sidebar:
        st.title({
            "Português": "Configurações",
            "English": "Settings",
            "Español": "Configuración"
        }[st.session_state.language])
        
        # Seletor de idioma
        selected_language = st.selectbox(
            {
                "Português": "Idioma",
                "English": "Language",
                "Español": "Idioma"
            }[st.session_state.language],
            options=["Português", "English", "Español"],
            index=["Português", "English", "Español"].index(st.session_state.language),
            key="language_selector"
        )
        st.session_state.language = selected_language
        
        # Seletor de moeda
        currency_labels = {
            "Português": {"BRL": "Real (R$)", "USD": "Dólar (US$)"},
            "English": {"BRL": "Brazilian Real (R$)", "USD": "US Dollar ($)"},
            "Español": {"BRL": "Real Brasileño (R$)", "USD": "Dólar Estadounidense ($)"}
        }
        
        selected_currency = st.selectbox(
            {
                "Português": "Moeda",
                "English": "Currency",
                "Español": "Moneda"
            }[st.session_state.language],
            options=["BRL", "USD"],
            format_func=lambda x: currency_labels[selected_language][x],
            index=["BRL", "USD"].index(st.session_state.currency),
            key="currency_selector"
        )
        st.session_state.currency = selected_currency
        
        # Seletor de tema
        selected_theme = st.selectbox(
            {
                "Português": "Tema",
                "English": "Theme",
                "Español": "Tema"
            }[st.session_state.language],
            options=["High Contrast", "Light", "Dark", "Blue", "Green"],
            index=["High Contrast", "Light", "Dark", "Blue", "Green"].index(st.session_state.theme),
            key="theme_selector"
        )
        st.session_state.theme = selected_theme
    
    return selected_theme, selected_language, selected_currency

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
            
            /* Campos monetários */
            .stNumberInputMask input {{
                font-family: monospace !important;
                font-size: 1.1em !important;
                padding-left: 2.2em !important;
                background-color: {colors["background"]} !important;
                color: {colors["text"]} !important;
                border: 1px solid {colors["accent"]} !important;
                border-radius: 4px !important;
            }}
            
            .stNumberInputMask .currency-prefix {{
                color: {colors["text"]} !important;
                opacity: 0.8;
                position: absolute;
                left: 0.8em;
                top: 50%;
                transform: translateY(-50%);
            }}
            
            .stNumberInputMask input:focus {{
                border-color: {colors["primary"]} !important;
                box-shadow: 0 0 0 1px {colors["primary"]} !important;
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

def render_input_form(language="Português", currency="BRL"):
    """Renderiza o formulário de entrada e retorna os valores inseridos."""
    translations = get_translations()[language]
    
    st.title(translations["titulo"])
    
    # Data de início fixa do fundo
    data_inicio = datetime(2024, 7, 1)
    
    # Seletor de período
    col1, col2 = st.columns(2)
    with col1:
        data_inicio_analise = st.date_input(
            "Data Inicial",
            value=data_inicio,
            min_value=data_inicio,
            max_value=date.today(),
            format="DD/MM/YYYY"
        )
    
    with col2:
        data_fim = st.date_input(
            "Data Final",
            value=date.today(),
            min_value=data_inicio,
            max_value=date.today(),
            format="DD/MM/YYYY"
        )
    
    # Configuração do formato da moeda
    currency_symbol = "R$" if currency == "BRL" else "$"
    
    # Campos de investimento
    capital_investido = st.number_input(
        f"{translations['capital_inicial']} ({currency_symbol})",
        min_value=0.0,
        value=10000.0,
        step=1000.0,
        format="%.2f"
    )
    
    retirada_mensal = st.number_input(
        f"{translations['retirada_mensal']} ({currency_symbol})",
        min_value=0.0,
        value=0.0,
        step=100.0,
        format="%.2f"
    )
    
    aporte_mensal = st.number_input(
        f"{translations['aporte_mensal']} ({currency_symbol})",
        min_value=0.0,
        value=0.0,
        step=100.0,
        format="%.2f"
    )
    
    reinvestir = st.checkbox(
        translations["reinvestir"],
        value=True,
        help=translations["reinvestir_help"]
    )
    
    return data_inicio_analise, data_fim, capital_investido, retirada_mensal, aporte_mensal, reinvestir

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

def render_results(df_resultado, dados_indicadores, indicadores_selecionados, language="Português", currency="BRL"):
    """Renderiza os resultados da simulação."""
    translations = get_translations()[language]
    
    st.subheader(translations["resultados"])
    
    # Exibindo o gráfico de evolução do capital
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_resultado.index, df_resultado['Saldo'], label=translations["capital_final"], linewidth=2)
    
    # Adicionando os indicadores selecionados ao gráfico
    for nome, tipo in indicadores_selecionados:
        if tipo == 'bcb':
            if nome in dados_indicadores:
                ax.plot(dados_indicadores[nome].index, dados_indicadores[nome]['valor'], label=nome, linestyle='--')
        elif tipo == 'yfinance':
            simbolo = dados_indicadores.get(nome)
            if simbolo is not None and simbolo in dados_indicadores:
                ax.plot(dados_indicadores[simbolo].index, dados_indicadores[simbolo]['retorno'], label=nome, linestyle='--')
    
    ax.set_title(translations["evolucao_capital"])
    ax.set_xlabel(translations["data_final"])
    ax.set_ylabel("Valor")
    ax.grid(True)
    ax.legend()
    
    st.pyplot(fig)
    
    # Exibindo estatísticas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            translations["capital_final"],
            formatar_moeda(df_resultado['Saldo'].iloc[-1], currency)
        )
    
    with col2:
        rentabilidade_total = (df_resultado['Saldo'].iloc[-1] / df_resultado['Capital'].iloc[0] - 1) * 100
        st.metric(
            translations["rentabilidade_total"],
            formatar_percentual(rentabilidade_total)
        )
    
    with col3:
        rentabilidade_media = df_resultado['Rentabilidade'].mean()
        st.metric(
            translations["rentabilidade_media"],
            formatar_percentual(rentabilidade_media)
        )
    
    # Exibindo a tabela de resultados
    st.dataframe(
        df_resultado.style.format({
            'Capital': lambda x: formatar_moeda(x, currency),
            'Retirada': lambda x: formatar_moeda(x, currency),
            'Aporte': lambda x: formatar_moeda(x, currency),
            'Saldo': lambda x: formatar_moeda(x, currency),
            'Rentabilidade': formatar_percentual
        }),
        use_container_width=True
    )

def get_translations():
    """Retorna as traduções para os textos da interface."""
    return {
        "Português": {
            "titulo": "Calculadora de Rentabilidade de Investimentos",
            "capital_inicial": "Capital Inicial",
            "aporte_mensal": "Aporte Mensal",
            "retirada_mensal": "Retirada Mensal",
            "data_final": "Data Final",
            "reinvestir": "Reinvestir Retiradas",
            "reinvestir_help": "Se marcado, as retiradas serão reinvestidas no próximo mês.",
            "indicadores": "Indicadores",
            "indicadores_bcb": "Indicadores BCB",
            "indicadores_bcb_help": "Selecione os indicadores do Banco Central do Brasil.",
            "indicadores_yfinance": "Indicadores YFinance",
            "indicadores_yfinance_help": "Selecione os indicadores do Yahoo Finance.",
            "calcular": "Calcular Rentabilidade",
            "resultados": "Resultados",
            "capital_final": "Capital Final",
            "rentabilidade_total": "Rentabilidade Total",
            "rentabilidade_media": "Rentabilidade Média Mensal",
            "evolucao_capital": "Evolução do Capital e Indicadores"
        },
        "English": {
            "titulo": "Investment Return Calculator",
            "capital_inicial": "Initial Capital",
            "aporte_mensal": "Monthly Contribution",
            "retirada_mensal": "Monthly Withdrawal",
            "data_final": "End Date",
            "reinvestir": "Reinvest Withdrawals",
            "reinvestir_help": "If checked, withdrawals will be reinvested next month.",
            "indicadores": "Indicators",
            "indicadores_bcb": "BCB Indicators",
            "indicadores_bcb_help": "Select Brazilian Central Bank indicators.",
            "indicadores_yfinance": "YFinance Indicators",
            "indicadores_yfinance_help": "Select Yahoo Finance indicators.",
            "calcular": "Calculate Returns",
            "resultados": "Results",
            "capital_final": "Final Capital",
            "rentabilidade_total": "Total Return",
            "rentabilidade_media": "Average Monthly Return",
            "evolucao_capital": "Capital and Indicators Evolution"
        },
        "Español": {
            "titulo": "Calculadora de Rentabilidad de Inversiones",
            "capital_inicial": "Capital Inicial",
            "aporte_mensal": "Aporte Mensual",
            "retirada_mensal": "Retiro Mensual",
            "data_final": "Fecha Final",
            "reinvestir": "Reinvertir Retiros",
            "reinvestir_help": "Si está marcado, los retiros se reinvertirán el próximo mes.",
            "indicadores": "Indicadores",
            "indicadores_bcb": "Indicadores BCB",
            "indicadores_bcb_help": "Seleccione los indicadores del Banco Central de Brasil.",
            "indicadores_yfinance": "Indicadores YFinance",
            "indicadores_yfinance_help": "Seleccione los indicadores de Yahoo Finance.",
            "calcular": "Calcular Rentabilidad",
            "resultados": "Resultados",
            "capital_final": "Capital Final",
            "rentabilidade_total": "Rentabilidad Total",
            "rentabilidade_media": "Rentabilidad Media Mensual",
            "evolucao_capital": "Evolución del Capital e Indicadores"
        }
    } 