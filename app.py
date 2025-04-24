import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date

# Importando os módulos criados
from bcb_api import obter_serie_bcb, proteger_dataframe
from cvm_api import obter_rentabilidade_fundo_cvm
from calculadora import calcular_rentabilidade_liquida

# Configuração da página
st.set_page_config(layout="wide")

# --- Interface Streamlit ---
st.title("Calculadora de Rentabilidade Líquida - Fundo Transfero")

# Inputs do usuário
capital_investido = st.number_input("Capital inicial investido (BRL)", value=1_500_000, step=10000)
retirada_mensal = st.number_input("Retirada mensal desejada (BRL)", value=70000, step=1000)
aporte_mensal = st.number_input("Aporte mensal (BRL)", value=0, step=1000)
reinvestir = st.checkbox("Reinvestir rendimentos?", value=False)

data_fim_input = st.date_input(
    "Data final da simulação", 
    value=date.today(), 
    min_value=date(2024, 7, 1), 
    max_value=date.today()
)

st.markdown("---")

st.info("Baixando dados da CVM e indicadores do BCB. Isso pode levar alguns segundos...")

# Configuração das datas
data_inicio = '01/07/2024'
data_fim_str = data_fim_input.strftime('%d/%m/%Y')

# Obtenção dos indicadores econômicos
cvm_cnpj = "54.776.432/0001-18"
df_cdi = obter_serie_bcb(4390, data_inicio, data_fim_str)
df_ibovespa = obter_serie_bcb(7, data_inicio, data_fim_str)
df_ipca = obter_serie_bcb(433, data_inicio, data_fim_str)
df_ifix = obter_serie_bcb(28501, data_inicio, data_fim_str)

# Ajuste de formatos
for df in [df_cdi, df_ibovespa, df_ipca, df_ifix]:
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
    
    # Exibição dos resultados
    st.dataframe(df_resultado.style.format({
        "Rentabilidade Bruta (%)": "{:.2f}",
        "CDI (%)": "{:.2f}",
        "Rentabilidade Líquida (%)": "{:.2f}",
        "Rendimento Líquido (BRL)": "R$ {:,.2f}",
        "Capital Final do Mês (BRL)": "R$ {:,.2f}"
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
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(df_resultado['Mês'], df_resultado['Rentabilidade Bruta (%)'], label='Fundo Transfero', marker='o')
    ax2.plot(df_cdi['ano_mes'], df_cdi['valor'], label='CDI', marker='x')
    ax2.plot(df_ibovespa['ano_mes'], df_ibovespa['valor'], label='IBOVESPA', marker='s')
    ax2.plot(df_ipca['ano_mes'], df_ipca['valor'], label='IPCA', marker='^')
    ax2.plot(df_ifix['ano_mes'], df_ifix['valor'], label='IFIX', marker='d')
    ax2.set_title("Rentabilidade Mensal: Fundo vs. Indicadores")
    ax2.set_xlabel("Mês")
    ax2.set_ylabel("Rentabilidade (%)")
    ax2.legend()
    ax2.grid(True)
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)
