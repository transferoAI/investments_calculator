###############################################################################
# Calculadora de Investimentos - Aplicação Principal
###############################################################################
# Este arquivo é o ponto de entrada da aplicação Streamlit.
# IMPORTANTE: Este arquivo deve ser mantido o mais simples possível,
# delegando a lógica para os módulos apropriados seguindo a Clean Architecture.
#
# Estrutura da Aplicação:
# 1. Importações (organizadas por camada)
# 2. Configuração inicial
# 3. Definição de constantes e configurações
# 4. Gerenciamento de estado
# 5. Interface do usuário
# 6. Lógica principal
#
# Clean Architecture:
# - Core: Lógica de negócio central (src/core)
# - Services: Integrações externas (src/services)
# - Web: Interface do usuário (src/web)
# - Utils: Utilitários e helpers (src/utils)
###############################################################################

# Importações necessárias
import streamlit as st
import pandas as pd
from datetime import date, datetime
import locale
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página Streamlit (deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="Monitoramento de Investimentos",
    page_icon="📈",
    layout="wide"
)

# Importações dos serviços
# NOTA: Todos os serviços devem implementar interfaces do core
from src.services.bcb_api import BCBDataFetcher
from src.services.yfinance_api import YFinanceDataFetcher
from src.services.cvm_api import CVMDataFetcher

# Importações do core
# NOTA: O core não deve depender de outras camadas
from src.core.investment_calculator import calcular_rentabilidade
from src.core.types import APIData, SimulationParameters, SimulationResults
from src.core.exceptions import APIError, CalculationError

# Importações da interface
# NOTA: A interface depende do core, mas não dos serviços
from src.web.components.theme import render_theme_selector, apply_theme
from src.web.pages.fund_data import render_fund_data_page

# Importação de constantes
from constants import FUNDO_CNPJ

from src.web.ui_components import (
    render_input_form,
    render_indicator_selector,
    render_results,
    formatar_moeda,
    formatar_percentual
)

# Importações de utilitários
# NOTA: Utilitários podem ser usados por qualquer camada
from src.utils.logging import project_logger
from src.utils.formatters import format_currency, format_percentage

###############################################################################
# Configuração inicial da aplicação
###############################################################################
# Esta seção configura aspectos básicos da aplicação
# IMPORTANTE: Manter configurações simples e delegar lógica complexa para outros módulos

# Configurando o locale para formatação de números em português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        st.warning("Não foi possível configurar o locale para português do Brasil. Os valores monetários podem não ser exibidos corretamente.")

###############################################################################
# Definição dos indicadores financeiros disponíveis
###############################################################################
# Esta seção define os indicadores que podem ser usados na simulação
# IMPORTANTE: Manter esta configuração separada da lógica de negócio

# Dicionário com códigos dos indicadores do Banco Central e Yahoo Finance
indicadores_disponiveis = {
    'bcb': {  # Indicadores do Banco Central do Brasil
        'CDI': 12,
        'Selic': 11,
        'IPCA': 433,
        'IGP-M': 189,
        'Poupança': 196
    },
    'yfinance': {  # Indicadores do Yahoo Finance
        'IBOVESPA': 'BVSP',
        'S&P 500': 'GSPC',
        'Dólar': 'BRL=X',
        'Ouro': 'GC=F'
    }
}

###############################################################################
# Gerenciamento do estado da aplicação
###############################################################################
# Esta seção gerencia o estado da aplicação usando o session_state do Streamlit
# IMPORTANTE: Manter o estado mínimo necessário e usar tipos definidos no core

# Inicialização das variáveis de estado do Streamlit
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'indicadores_selecionados' not in st.session_state:
    st.session_state.indicadores_selecionados = []
if 'dados_indicadores' not in st.session_state:
    st.session_state.dados_indicadores = {}

# Inicialização do histórico de simulações
if 'historico_simulacoes' not in st.session_state:
    st.session_state.historico_simulacoes = []

###############################################################################
# Interface do usuário
###############################################################################
# Esta seção renderiza os componentes da interface
# IMPORTANTE: Manter a interface separada da lógica de negócio

# Renderização dos componentes de UI
st.title("📊 Calculadora de Investimentos")
theme, mostrar_tendencias, mostrar_estatisticas, mostrar_alertas, formato_exportacao = render_theme_selector()
apply_theme(theme)

# Abas principais do app
abas = st.tabs(["Simulação", "Histórico de Simulações", "Rentabilidade do Fundo"])

with abas[0]:
    # Aba de Simulação (fluxo principal)
    resultado_form = render_input_form()

    if resultado_form:
        # Desempacotando os valores do formulário
        data_inicio_analise, data_fim, capital_investido, retirada_mensal, aporte_mensal, reinvestir = resultado_form
        
        # Seleção de indicadores para comparação
        indicadores_selecionados, calcular = render_indicator_selector(indicadores_disponiveis)

        # Processamento dos cálculos quando o botão é pressionado
        if calcular:
            # Inicialização da barra de progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            ###############################################################################
            # Coleta de dados
            ###############################################################################
            # Esta seção obtém dados de diferentes fontes
            # IMPORTANTE: Usar as classes fetcher que implementam interfaces do core
            
            # 1. Dados do fundo de investimento
            status_text.text("Obtendo dados do fundo...")
            progress_bar.progress(10)
            cvm_fetcher = CVMDataFetcher()
            dados_fundo = cvm_fetcher.fetch_data(data_inicio_analise, data_fim)
            
            # 2. Dados do Banco Central
            status_text.text("Obtendo dados do Banco Central do Brasil...")
            bcb_fetcher = BCBDataFetcher()
            dados_bcb = {}
            for nome, codigo in indicadores_disponiveis['bcb'].items():
                if nome in [ind[0] for ind in indicadores_selecionados if ind[1] == 'bcb']:
                    dados = bcb_fetcher.fetch_data([codigo], data_fim)
                    if dados is not None:
                        dados_bcb[nome] = dados
            
            progress_bar.progress(40)
            
            # 3. Dados do Yahoo Finance
            status_text.text("Obtendo dados do Yahoo Finance...")
            yf_fetcher = YFinanceDataFetcher()
            dados_yfinance = {}
            for nome, simbolo in indicadores_disponiveis['yfinance'].items():
                if nome in [ind[0] for ind in indicadores_selecionados if ind[1] == 'yfinance']:
                    dados = yf_fetcher.fetch_data([simbolo], data_fim)
                    if dados is not None:
                        dados_yfinance[simbolo] = dados
            
            progress_bar.progress(70)
            
            ###############################################################################
            # Processamento dos dados
            ###############################################################################
            # Esta seção processa e combina os dados
            # IMPORTANTE: Usar funções do core para processamento
            
            # Combinando todos os dados dos indicadores
            status_text.text("Combinando dados dos indicadores...")
            dados_indicadores = {**dados_bcb, **dados_yfinance}
            
            progress_bar.progress(80)
            
            # Cálculo final da rentabilidade
            status_text.text("Calculando a rentabilidade...")
            try:
                df_resultado = calcular_rentabilidade(
                    capital_investido=capital_investido,
                    retirada_mensal=retirada_mensal,
                    aporte_mensal=aporte_mensal,
                    data_fim=data_fim,
                    reinvestir=reinvestir,
                    dados_indicadores=dados_indicadores
                )
            except CalculationError as e:
                st.error(f"Erro ao calcular rentabilidade: {str(e)}")
                st.stop()
            
            ###############################################################################
            # Atualização do estado e exibição dos resultados
            ###############################################################################
            # Esta seção atualiza o estado e exibe os resultados
            # IMPORTANTE: Usar componentes UI para exibição
            
            # Salvando resultados no estado da sessão
            status_text.text("Finalizando o cálculo...")
            st.session_state.resultados = df_resultado
            st.session_state.indicadores_selecionados = indicadores_selecionados
            st.session_state.dados_indicadores = dados_indicadores
            
            progress_bar.progress(100)
            status_text.text("Cálculo concluído!")
            
            # Exibição dos resultados
            render_results(df_resultado, dados_indicadores, indicadores_selecionados, language, currency)
            
            ###############################################################################
            # Exportação dos resultados
            ###############################################################################
            # Esta seção lida com a exportação dos resultados
            # IMPORTANTE: Usar utilitários para formatação e exportação
            
            # Botão para exportar resultados em CSV
            if st.button("Exportar Resultados"):
                # Preparação do DataFrame para exportação
                df_export = df_resultado.copy()
                
                # Formatação das colunas monetárias
                df_export['Capital'] = df_export['Capital'].apply(format_currency)
                df_export['Retirada'] = df_export['Retirada'].apply(format_currency)
                df_export['Aporte'] = df_export['Aporte'].apply(format_currency)
                df_export['Saldo'] = df_export['Saldo'].apply(format_currency)
                df_export['Rentabilidade'] = df_export['Rentabilidade'].apply(format_percentage)
                
                # Adição dos indicadores selecionados ao DataFrame
                for nome, tipo in indicadores_selecionados:
                    if tipo == 'bcb':
                        if nome in dados_indicadores:
                            df_export[nome] = dados_indicadores[nome]['valor'].apply(format_percentage)
                    elif tipo == 'yfinance':
                        simbolo = dados_indicadores.get(nome)
                        if simbolo is not None and simbolo in dados_indicadores:
                            df_export[nome] = dados_indicadores[simbolo]['retorno'].apply(format_percentage)
                
                # Geração e download do arquivo CSV
                csv = df_export.to_csv(index=True).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            # Após calcular e exibir resultados, salvar no histórico:
            sim_data = {
                'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'parametros': {
                    'data_inicio_analise': data_inicio_analise,
                    'data_fim': data_fim,
                    'capital_investido': capital_investido,
                    'retirada_mensal': retirada_mensal,
                    'aporte_mensal': aporte_mensal,
                    'reinvestir': reinvestir,
                    'indicadores': indicadores_selecionados
                },
                'resultados': df_resultado.copy()
            }
            st.session_state.historico_simulacoes.append(sim_data)
    else:
        st.info("Preencha os campos acima e clique em 'Calcular Rentabilidade' para ver os resultados.")

with abas[1]:
    st.header("Histórico de Simulações")
    historico = st.session_state.get('historico_simulacoes', [])
    if historico:
        # Monta DataFrame resumido para exibição
        df_hist = pd.DataFrame([
            {
                'Data/Hora': sim['data_hora'],
                'Capital Inicial': sim['parametros']['capital_investido'],
                'Aporte Mensal': sim['parametros']['aporte_mensal'],
                'Retirada Mensal': sim['parametros']['retirada_mensal'],
                'Indicadores': ', '.join([str(i) for i in sim['parametros']['indicadores']]),
                'Capital Final': sim['resultados']['Saldo'].iloc[-1] if 'Saldo' in sim['resultados'] else None
            }
            for sim in historico
        ])
        st.dataframe(df_hist, use_container_width=True)
        # Botão para exportar histórico
        csv_hist = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Exportar Histórico (CSV)",
            data=csv_hist,
            file_name=f"historico_simulacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhuma simulação realizada ainda.")

with abas[2]:
    # -------------------------------------------------------------------
    # Aba de Rentabilidade do Fundo
    #
    # Esta aba permite visualizar e atualizar os dados de rentabilidade
    # do fundo de investimento. Ela oferece:
    #
    # 1. Atualização dos dados via CVM
    # 2. Visualização do progresso do download
    # 3. Exibição dos dados em diferentes periodicidades
    # 4. Gráfico de evolução do valor da cota
    #
    # IMPORTANTE:
    # - O download é incremental e idempotente
    # - O progresso é atualizado em tempo real
    # - Os dados são persistidos localmente
    # -------------------------------------------------------------------
    render_fund_data_page()
