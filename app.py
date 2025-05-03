###############################################################################
# Calculadora de Investimentos - Aplicação Principal
###############################################################################
# Este arquivo contém a aplicação Streamlit principal que permite aos usuários:
# 1. Calcular rentabilidade de investimentos
# 2. Comparar com diferentes indicadores financeiros
# 3. Visualizar resultados em formato tabular e gráfico
# 4. Exportar resultados para CSV
###############################################################################

# Importações necessárias
import streamlit as st
import pandas as pd
from datetime import date, datetime
import locale
from bcb_api import obter_dados_bcb
# Removendo a importação da função que não existe
# from cvm_api import obter_dados_cvm
from calculadora import calcular_rentabilidade
from ui_components import (
    render_theme_selector,
    apply_theme,
    render_input_form,
    render_indicator_selector,
    render_results,
    formatar_moeda,
    formatar_percentual
)
from yfinance_api import obter_dados_yfinance
from cvm_api import obter_rentabilidade_fundo_cvm

###############################################################################
# Configuração inicial da aplicação
###############################################################################

# Configurando o locale para formatação de números em português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        st.warning("Não foi possível configurar o locale para português do Brasil. Os valores monetários podem não ser exibidos corretamente.")

# Configuração da página Streamlit
st.set_page_config(
    page_title="Monitoramento de Investimentos",
    page_icon="📈",
    layout="wide"
)

###############################################################################
# Definição dos indicadores financeiros disponíveis
###############################################################################

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
        'IBOVESPA': '^BVSP',
        'S&P 500': '^GSPC',
        'Dólar': 'BRL=X',
        'Ouro': 'GC=F'
    }
}

###############################################################################
# Gerenciamento do estado da aplicação
###############################################################################

# Inicialização das variáveis de estado do Streamlit
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'indicadores_selecionados' not in st.session_state:
    st.session_state.indicadores_selecionados = []
if 'dados_indicadores' not in st.session_state:
    st.session_state.dados_indicadores = {}

###############################################################################
# Interface do usuário
###############################################################################

# Renderização dos componentes de UI
theme, language, currency = render_theme_selector()
apply_theme(theme)

# Formulário principal para entrada de dados
resultado_form = render_input_form(language, currency)

###############################################################################
# Lógica principal da aplicação
###############################################################################

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
        
        # 1. Dados do fundo de investimento
        status_text.text("Obtendo dados do fundo...")
        progress_bar.progress(10)
        dados_fundo = obter_rentabilidade_fundo_cvm(data_inicio_analise, data_fim)
        
        # 2. Dados do Banco Central
        status_text.text("Obtendo dados do Banco Central do Brasil...")
        dados_bcb = {}
        for nome, codigo in indicadores_disponiveis['bcb'].items():
            if nome in [ind[0] for ind in indicadores_selecionados if ind[1] == 'bcb']:
                dados = obter_dados_bcb(codigo, data_fim)
                if dados is not None:
                    dados_bcb[nome] = dados
        
        progress_bar.progress(40)
        
        # 3. Dados do Yahoo Finance
        status_text.text("Obtendo dados do Yahoo Finance...")
        dados_yfinance = {}
        for nome, simbolo in indicadores_disponiveis['yfinance'].items():
            if nome in [ind[0] for ind in indicadores_selecionados if ind[1] == 'yfinance']:
                dados = obter_dados_yfinance(simbolo, data_fim)
                if dados is not None:
                    dados_yfinance[simbolo] = dados
        
        progress_bar.progress(70)
        
        ###############################################################################
        # Processamento dos dados
        ###############################################################################
        
        # Combinando todos os dados dos indicadores
        status_text.text("Combinando dados dos indicadores...")
        dados_indicadores = {**dados_bcb, **dados_yfinance}
        
        progress_bar.progress(80)
        
        # Cálculo final da rentabilidade
        status_text.text("Calculando a rentabilidade...")
        df_resultado = calcular_rentabilidade(
            capital_investido=capital_investido,
            retirada_mensal=retirada_mensal,
            aporte_mensal=aporte_mensal,
            data_fim=data_fim,
            reinvestir=reinvestir,
            dados_indicadores=dados_indicadores
        )
        
        ###############################################################################
        # Atualização do estado e exibição dos resultados
        ###############################################################################
        
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
        
        # Botão para exportar resultados em CSV
        if st.button("Exportar Resultados"):
            # Preparação do DataFrame para exportação
            df_export = df_resultado.copy()
            
            # Formatação das colunas monetárias
            df_export['Capital'] = df_export['Capital'].apply(formatar_moeda)
            df_export['Retirada'] = df_export['Retirada'].apply(formatar_moeda)
            df_export['Aporte'] = df_export['Aporte'].apply(formatar_moeda)
            df_export['Saldo'] = df_export['Saldo'].apply(formatar_moeda)
            df_export['Rentabilidade'] = df_export['Rentabilidade'].apply(formatar_percentual)
            
            # Adição dos indicadores selecionados ao DataFrame
            for nome, tipo in indicadores_selecionados:
                if tipo == 'bcb':
                    if nome in dados_indicadores:
                        df_export[nome] = dados_indicadores[nome]['valor'].apply(formatar_percentual)
                elif tipo == 'yfinance':
                    simbolo = dados_indicadores.get(nome)
                    if simbolo is not None and simbolo in dados_indicadores:
                        df_export[nome] = dados_indicadores[simbolo]['retorno'].apply(formatar_percentual)
            
            # Geração e download do arquivo CSV
            csv = df_export.to_csv(index=True).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
else:
    st.info("Preencha os campos acima e clique em 'Calcular Rentabilidade' para ver os resultados.")
