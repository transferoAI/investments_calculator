"""
Aplicação principal Streamlit.

Este módulo é o ponto de entrada da aplicação e gerencia a navegação entre páginas.
"""

import streamlit as st
import os

from src.web.pages.simulation import render_simulation_page
from src.web.pages.history import render_history_page
from src.web.pages.fund_data import render_fund_data_page
from src.web.components.theme import render_theme_selector, apply_theme

# Carrega o CSS
def load_css():
    """Carrega os estilos CSS da aplicação."""
    css_path = os.path.join(os.path.dirname(__file__), 'assets', 'styles.css')
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Configuração da página
st.set_page_config(
    page_title="Monitoramento de Investimentos",
    page_icon="📈",
    layout="wide"
)

# Carrega os estilos
load_css()

# Aplica o tema escuro por padrão
st.markdown("""
    <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
    </style>
""", unsafe_allow_html=True)

# Renderização do seletor de tema
theme, mostrar_tendencias, mostrar_estatisticas, mostrar_alertas, formato_exportacao = render_theme_selector()
apply_theme(theme)

# Título principal
st.title("📊 Calculadora de Investimentos")

# Abas principais
abas = st.tabs(["Simulação", "Histórico de Simulações", "Rentabilidade do Fundo"])

# Renderiza cada página em sua respectiva aba
with abas[0]:
    render_simulation_page()

with abas[1]:
    render_history_page()

with abas[2]:
    render_fund_data_page()
