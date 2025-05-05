"""
Módulo de componentes de tema.

Este módulo contém os componentes relacionados à personalização do tema da aplicação.
"""

import streamlit as st

def render_theme_selector():
    """
    Renderiza o seletor de tema e opções de visualização.
    
    Returns:
        Tuple contendo:
        - theme: Tema selecionado
        - mostrar_tendencias: Se deve mostrar tendências
        - mostrar_estatisticas: Se deve mostrar estatísticas
        - mostrar_alertas: Se deve mostrar alertas
        - formato_exportacao: Formato de exportação selecionado
    """
    # Seção de personalização
    st.sidebar.header("Personalização")
    
    # Seletor de tema
    theme = st.sidebar.selectbox(
        "Tema",
        options=["Escuro", "Claro", "Sistema"],
        index=0,  # Escuro como padrão
        help="Selecione o tema da aplicação"
    )
    
    # Opções de visualização
    st.sidebar.subheader("Visualização")
    mostrar_tendencias = st.sidebar.checkbox(
        "Mostrar Tendências",
        value=True,
        help="Exibe tendências nos gráficos"
    )
    mostrar_estatisticas = st.sidebar.checkbox(
        "Mostrar Estatísticas",
        value=True,
        help="Exibe estatísticas detalhadas"
    )
    mostrar_alertas = st.sidebar.checkbox(
        "Mostrar Alertas",
        value=True,
        help="Exibe alertas e notificações"
    )
    
    # Formato de exportação
    st.sidebar.subheader("Exportação")
    formato_exportacao = st.sidebar.selectbox(
        "Formato de Exportação",
        options=["CSV", "Excel", "JSON"],
        index=0,
        help="Selecione o formato para exportar dados"
    )
    
    return theme, mostrar_tendencias, mostrar_estatisticas, mostrar_alertas, formato_exportacao

def apply_theme(theme: str):
    """
    Aplica o tema selecionado à aplicação.
    
    Args:
        theme: Nome do tema a ser aplicado
    """
    if theme == "Escuro":
        st.markdown("""
            <style>
                .stApp {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
            </style>
        """, unsafe_allow_html=True)
    elif theme == "Claro":
        st.markdown("""
            <style>
                .stApp {
                    background-color: #FFFFFF;
                    color: #000000;
                }
            </style>
        """, unsafe_allow_html=True)
    # Para "Sistema", não aplicamos nenhum estilo específico 