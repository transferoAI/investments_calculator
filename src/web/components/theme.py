import streamlit as st

def render_theme_selector():
    """Renderiza o seletor de tema e retorna o tema selecionado."""
    with st.sidebar:
        st.title("⚙️ Configurações")
        theme = st.selectbox(
            "🎨 Tema",
            ["Claro", "Escuro"],
            index=1,  # Escuro como padrão
            help="Selecione o tema da interface"
        )
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

def apply_theme(theme: str) -> None:
    """
    Aplica o tema da aplicação.
    """
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {'#f5f5f5' if theme == 'Claro' else '#0f172a'};
        color: {'#222222' if theme == 'Claro' else '#f8fafc'};
    }}
    .stButton>button {{
        background-color: #2563eb;
        color: #fff;
    }}
    .stButton>button:hover {{
        background-color: #1e40af;
    }}
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stCheckbox > div > div > label,
    .stSelectbox > div > div > select {{
        background-color: #fff;
        color: #222;
        border: 1px solid #bbb;
    }}
    /* Labels dos campos */
    label, .stTextInput label, .stNumberInput label, .stDateInput label, .stSelectbox label {{
        color: {'#222222' if theme == 'Claro' else '#f8fafc'} !important;
        font-weight: 600;
    }}
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
        color: {'#1e40af' if theme == 'Claro' else '#2563eb'};
    }}
    </style>
    """, unsafe_allow_html=True) 