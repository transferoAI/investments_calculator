import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date

# Importando os módulos criados
from bcb_api import obter_serie_bcb
from cvm_api import obter_rentabilidade_fundo_cvm
from calculadora import calcular_rentabilidade_liquida
from yfinance_api import obter_dados_yfinance

# Configuração da página
st.set_page_config(layout="wide")

# Função para formatar valores monetários no formato brasileiro
def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira (R$).
    
    Args:
        valor (float): Valor a ser formatado
        
    Returns:
        str: Valor formatado como moeda brasileira (ex: R$ 1.234,56)
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- Interface Streamlit ---
st.title("Monitoramento de Investimentos")
st.subheader("Transfero Horizon")

# Criando colunas para organizar os inputs
col1, col2 = st.columns(2)

with col1:
    # Inputs do usuário com formatação de moeda
    capital_investido = st.number_input(
        "Capital inicial investido (BRL)", 
        value=1_500_000, 
        step=10000,
        format="%d"
    )
    
    retirada_mensal = st.number_input(
        "Retirada mensal desejada (BRL)", 
        value=70000, 
        step=1000,
        format="%d"
    )
    
    aporte_mensal = st.number_input(
        "Aporte mensal (BRL)", 
        value=0, 
        step=1000,
        format="%d"
    )

with col2:
    # Data no formato brasileiro
    data_fim_input = st.date_input(
        "Data final da simulação", 
        value=date.today(), 
        min_value=date(2024, 7, 1), 
        max_value=date.today(),
        format="DD/MM/YYYY"
    )
    
    reinvestir = st.checkbox("Reinvestir rendimentos?", value=False)

# Botão para executar o cálculo
calcular = st.button("Calcular Rentabilidade", type="primary")

st.markdown("---")

if calcular:
    st.info("Baixando dados da CVM, YFinance e indicadores do BCB. Isso pode levar alguns segundos...")

    # Configuração das datas
    data_inicio = '01/07/2024'
    data_fim_str = data_fim_input.strftime('%d/%m/%Y')

    # Obtenção dos indicadores econômicos
    cvm_cnpj = "54.776.432/0001-18"
    df_cdi = obter_serie_bcb(4390, data_inicio, data_fim_str)
    df_ipca = obter_serie_bcb(433, data_inicio, data_fim_str)
    df_selic = obter_serie_bcb(11, data_inicio, data_fim_str)
    
    # Usando a função genérica para obter dados do YFinance
    df_ibovespa = obter_dados_yfinance('^BVSP', data_inicio, data_fim_str)
    df_sp500 = obter_dados_yfinance('^GSPC', data_inicio, data_fim_str)
    df_dolar = obter_dados_yfinance('BRL=X', data_inicio, data_fim_str)
    df_ouro = obter_dados_yfinance('GC=F', data_inicio, data_fim_str)
    
    

    # Ajuste de formatos
    for df in [df_cdi, df_ipca, df_selic]:
        df['ano_mes'] = df['ano_mes'].astype(str)

    # Preparação do range de datas
    data_inicio_obj = datetime.strptime("2024-07", "%Y-%m")
    data_fim_obj = datetime(data_fim_input.year, data_fim_input.month, 1)
    data_range = pd.date_range(start=data_inicio_obj, end=data_fim_obj, freq='MS')
    datas_desejadas = [d.strftime("%Y-%m") for d in data_range]

    # Obtenção dos dados do fundo
    dados_fundo = obter_rentabilidade_fundo_cvm(cvm_cnpj, datas_desejadas)

    if not dados_fundo:
        st.error("Não foi possível obter os dados do fundo.")
    else:
        # Cálculo da rentabilidade
        df_resultado = calcular_rentabilidade_liquida(
            dados_fundo, df_cdi, capital_investido,
            retirada_mensal, aporte_mensal, reinvestir
        )

        st.success("Cálculo finalizado!")
        
        # Exibição dos resultados com formatação de moeda
        st.dataframe(df_resultado.style.format({
            "Rentabilidade Bruta (%)": "{:.2f}",
            "CDI (%)": "{:.2f}",
            "Rentabilidade Líquida (%)": "{:.2f}",
            "Rendimento Líquido (BRL)": lambda x: formatar_moeda(x),
            "Capital Final do Mês (BRL)": lambda x: formatar_moeda(x)
        }))

        # Gráfico de evolução do capital
        st.markdown("### Evolução do Capital ao Longo do Tempo")
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        ax1.plot(df_resultado['Mês'], df_resultado['Capital Final do Mês (BRL)'], marker='o')
        ax1.set_title("Evolução do Capital Final por Mês")
        ax1.set_xlabel("Mês")
        ax1.set_ylabel("Capital (R$)")
        ax1.tick_params(axis='x', rotation=45)
        st.pyplot(fig1)

        # Gráfico comparativo de rentabilidade
        st.markdown("### Comparativo de Rentabilidade Mensal")
        df_resultado['Mês'] = pd.PeriodIndex(df_resultado['Mês'], freq='M').astype(str)
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.plot(df_resultado['Mês'], df_resultado['Rentabilidade Bruta (%)'], label='Fundo Transfero', marker='o')
        ax2.plot(df_cdi['ano_mes'], df_cdi['valor'], label='CDI', marker='x')
        ax2.plot(df_ibovespa['ano_mes'], df_ibovespa['valor'], label='IBOVESPA', marker='s')
        ax2.plot(df_sp500['ano_mes'], df_sp500['valor'], label='S&P 500', marker='^')
        ax2.plot(df_dolar['ano_mes'], df_dolar['valor'], label='Dólar', marker='d')
        ax2.plot(df_ouro['ano_mes'], df_ouro['valor'], label='Ouro', marker='*')
        ax2.plot(df_ipca['ano_mes'], df_ipca['valor'], label='IPCA', marker='v')
        ax2.plot(df_selic['ano_mes'], df_selic['valor'], label='SELIC', marker='<')
        ax2.set_title("Rentabilidade Mensal: Fundo vs. Indicadores")
        ax2.set_xlabel("Mês")
        ax2.set_ylabel("Rentabilidade (%)")
        ax2.legend()
        ax2.grid(True)
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)
else:
    st.info("Clique no botão 'Calcular Rentabilidade' para iniciar a simulação.")
