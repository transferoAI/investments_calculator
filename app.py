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

# Configurando o locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        st.warning("Não foi possível configurar o locale para português do Brasil. Os valores monetários podem não ser exibidos corretamente.")

# Configurando a página
st.set_page_config(
    page_title="Monitoramento de Investimentos",
    page_icon="📈",
    layout="wide"
)

# Definindo os indicadores disponíveis
indicadores_disponiveis = {
    'bcb': {
        'CDI': 12,
        'Selic': 11,
        'IPCA': 433,
        'IGP-M': 189,
        'Poupança': 196
    },
    'yfinance': {
        'IBOVESPA': '^BVSP',
        'S&P 500': '^GSPC',
        'Dólar': 'BRL=X',
        'Ouro': 'GC=F'
    }
}

# Inicializando o estado da sessão
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'indicadores_selecionados' not in st.session_state:
    st.session_state.indicadores_selecionados = []
if 'dados_indicadores' not in st.session_state:
    st.session_state.dados_indicadores = {}

# Renderizando o seletor de tema
theme = render_theme_selector()
apply_theme(theme)

# Renderizando o formulário de entrada
capital_investido, retirada_mensal, aporte_mensal, data_fim, reinvestir = render_input_form()

# Renderizando o seletor de indicadores
indicadores_selecionados, calcular = render_indicator_selector(indicadores_disponiveis)

# Verificando se o botão de cálculo foi pressionado ou se já existem resultados
if calcular or st.session_state.resultados is not None:
    # Criando uma barra de progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Atualizando o status
    status_text.text("Iniciando o cálculo de rentabilidade...")
    progress_bar.progress(10)
    
    # Obtendo os dados do BCB
    status_text.text("Obtendo dados do Banco Central do Brasil...")
    dados_bcb = {}
    for nome, codigo in indicadores_disponiveis['bcb'].items():
        if nome in [ind[0] for ind in indicadores_selecionados if ind[1] == 'bcb']:
            dados = obter_dados_bcb(codigo, data_fim)
            if dados is not None:
                dados_bcb[nome] = dados
    
    progress_bar.progress(40)
    
    # Obtendo os dados do YFinance
    status_text.text("Obtendo dados do Yahoo Finance...")
    dados_yfinance = {}
    for nome, simbolo in indicadores_disponiveis['yfinance'].items():
        if nome in [ind[0] for ind in indicadores_selecionados if ind[1] == 'yfinance']:
            dados = obter_dados_yfinance(simbolo, data_fim)
            if dados is not None:
                dados_yfinance[simbolo] = dados
    
    progress_bar.progress(70)
    
    # Combinando os dados dos indicadores
    status_text.text("Combinando dados dos indicadores...")
    dados_indicadores = {**dados_bcb, **dados_yfinance}
    
    progress_bar.progress(80)
    
    # Calculando a rentabilidade
    status_text.text("Calculando a rentabilidade...")
    df_resultado = calcular_rentabilidade(
        capital_investido=capital_investido,
        retirada_mensal=retirada_mensal,
        aporte_mensal=aporte_mensal,
        data_fim=data_fim,
        reinvestir=reinvestir,
        dados_indicadores=dados_indicadores
    )
    
    progress_bar.progress(90)
    
    # Salvando os resultados no estado da sessão
    status_text.text("Finalizando o cálculo...")
    st.session_state.resultados = df_resultado
    st.session_state.indicadores_selecionados = indicadores_selecionados
    st.session_state.dados_indicadores = dados_indicadores
    
    progress_bar.progress(100)
    status_text.text("Cálculo concluído!")
    
    # Renderizando os resultados
    render_results(df_resultado, dados_indicadores, indicadores_selecionados)
    
    # Adicionando botão para exportar resultados
    if st.button("Exportar Resultados"):
        # Preparando o DataFrame para exportação
        df_export = df_resultado.copy()
        df_export['Capital'] = df_export['Capital'].apply(formatar_moeda)
        df_export['Retirada'] = df_export['Retirada'].apply(formatar_moeda)
        df_export['Aporte'] = df_export['Aporte'].apply(formatar_moeda)
        df_export['Saldo'] = df_export['Saldo'].apply(formatar_moeda)
        df_export['Rentabilidade'] = df_export['Rentabilidade'].apply(formatar_percentual)
        
        # Adicionando os indicadores selecionados
        for nome, tipo in indicadores_selecionados:
            if tipo == 'bcb':
                if nome in dados_indicadores:
                    df_export[nome] = dados_indicadores[nome]['valor'].apply(formatar_percentual)
            elif tipo == 'yfinance':
                simbolo = dados_indicadores.get(nome)
                if simbolo is not None and simbolo in dados_indicadores:
                    df_export[nome] = dados_indicadores[simbolo]['retorno'].apply(formatar_percentual)
        
        # Convertendo para CSV
        csv = df_export.to_csv(index=True).encode('utf-8')
        
        # Criando o botão de download
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
else:
    st.info("Preencha os campos acima e clique em 'Calcular Rentabilidade' para ver os resultados.")
