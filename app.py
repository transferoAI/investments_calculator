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
from historico_simulacoes import HistoricoSimulacoes

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

def main():
    """Função principal da aplicação."""
    # Inicializando o histórico
    historico = HistoricoSimulacoes()
    
    # Configurando a página
    st.set_page_config(
        page_title="Monitoramento de Investimentos",
        page_icon="",
        layout="wide"
    )
    
    # Renderizando o seletor de tema
    theme = render_theme_selector()
    apply_theme(theme)
    
    # Sidebar com opções
    with st.sidebar:
        st.title("")
        pagina = st.radio(
            "Selecione a página",
            ["Calculadora", "Dashboard", "Histórico"],
            index=0
        )
    
    if pagina == "Calculadora":
        # Renderizando o formulário de entrada
        capital_investido, retirada_mensal, aporte_mensal, data_fim, reinvestir, taxa_inflacao, taxa_risco = render_input_form()
        
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
            
            # Calculando a rentabilidade
            status_text.text("Calculando rentabilidade...")
            df_resultado = calcular_rentabilidade(
                capital_investido,
                retirada_mensal,
                aporte_mensal,
                data_fim,
                reinvestir,
                {**dados_bcb, **dados_yfinance}
            )
            
            progress_bar.progress(100)
            status_text.text("Cálculo concluído!")
            
            # Salvando os resultados no histórico
            resultados = {
                'capital_inicial': capital_investido,
                'retirada_mensal': retirada_mensal,
                'aporte_mensal': aporte_mensal,
                'data_fim': data_fim,
                'reinvestir': reinvestir,
                'taxa_inflacao': taxa_inflacao,
                'taxa_risco': taxa_risco,
                'capital_final': df_resultado['Saldo'].iloc[-1],
                'rentabilidade_total': (df_resultado['Saldo'].iloc[-1] / df_resultado['Capital'].iloc[0] - 1) * 100,
                'volatilidade': df_resultado['Saldo'].pct_change().std() * 100,
                'indice_sharpe': (df_resultado['Saldo'].iloc[-1] / df_resultado['Capital'].iloc[0] - 1 - 0.0225) / (df_resultado['Saldo'].pct_change().std() * 100),
                'indicadores': [ind[0] for ind in indicadores_selecionados]
            }
            
            historico.adicionar_simulacao(resultados)
            
            # Renderizando os resultados
            render_results(df_resultado, {**dados_bcb, **dados_yfinance}, indicadores_selecionados)
    
    elif pagina == "Dashboard":
        st.markdown("# ")
        st.markdown("")
        
        # Exibindo o dashboard
        criar_dashboard()
    
    else:  # Histórico
        st.markdown("# ")
        
        # Exibindo o histórico
        todas_simulacoes = historico.obter_historico()
        
        if todas_simulacoes:
            # Criando DataFrame com todas as simulações
            df_historico = pd.DataFrame([
                {
                    'Data': sim['data'],
                    'Capital Inicial': sim['parametros']['capital_inicial'],
                    'Capital Final': sim['resultados']['capital_final'],
                    'Rentabilidade': sim['resultados']['rentabilidade_total'],
                    'Volatilidade': sim['resultados']['volatilidade'],
                    'Índice Sharpe': sim['resultados']['indice_sharpe']
                }
                for sim in todas_simulacoes
            ])
            
            # Exibindo tabela
            st.dataframe(
                df_historico.style.format({
                    'Capital Inicial': formatar_moeda,
                    'Capital Final': formatar_moeda,
                    'Rentabilidade': formatar_percentual,
                    'Volatilidade': formatar_percentual,
                    'Índice Sharpe': '{:.2f}'
                }),
                use_container_width=True
            )
            
            # Botão para exportar histórico
            if st.button(""):
                df_historico.to_excel("historico_simulacoes.xlsx", index=False)
                st.success("")
        else:
            st.info("")

if __name__ == "__main__":
    main()
