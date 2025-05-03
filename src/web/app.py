"""
Aplicativo principal da Calculadora de Investimentos.

Este módulo é o ponto de entrada do aplicativo web.
"""

import streamlit as st
from src.core.interfaces import IUIComponent
from src.web.ui_components import render_input_form, render_results, render_dashboard
from src.services.investment_calculator import InvestmentCalculator
from src.data.historico_simulacoes import HistoricoSimulacoes
from src.utils.logging import project_logger

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Investimentos",
    page_icon="💰",
    layout="wide"
)

class MainApp(IUIComponent):
    """Classe principal do aplicativo."""
    
    def __init__(self):
        """Inicializa o aplicativo."""
        self.calculator = InvestmentCalculator()
        self.historico = HistoricoSimulacoes()
        self.logger = project_logger
        
    def render(self):
        """Renderiza o aplicativo."""
        try:
            # Barra lateral
            with st.sidebar:
                st.title("⚙️ Configurações")
                tema = st.selectbox(
                    "Tema",
                    ["Claro", "Escuro"],
                    index=1
                )
                
            # Página principal
            st.title("💰 Calculadora de Investimentos")
            
            # Renderiza o formulário de entrada
            input_data = render_input_form()
            
            if st.button("Calcular Rentabilidade"):
                if input_data:
                    # Calcula os resultados
                    results = self.calculator.calculate(input_data)
                    
                    # Renderiza os resultados
                    render_results(results['df_resultado'],
                                  results['indicadores_selecionados'],
                                  results['mostrar_tendencias'],
                                  results['mostrar_estatisticas'])
                    
                    # Adiciona ao histórico
                    self.historico.add_simulation({
                        'data': str(input_data['data_fim']),
                        'parametros': input_data,
                        'resultados': results,
                        'indicadores': input_data['indicadores_selecionados']
                    })
                else:
                    st.warning("Por favor, preencha os dados do formulário primeiro.")
                
        except Exception as e:
            self.logger.error(f"Erro ao renderizar aplicativo: {str(e)}")
            st.error(f"Ocorreu um erro: {str(e)}")

if __name__ == "__main__":
    app = MainApp()
    app.render()
