import pandas as pd
import requests
from datetime import datetime, date
import zipfile
import io
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# --- Funções ---
def obter_serie_bcb(codigo_serie, data_inicio, data_fim):
    try:
        url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}'
        response = requests.get(url)
        response.raise_for_status()
        dados = response.json()
        df = pd.DataFrame(dados)
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        df['valor'] = df['valor'].astype(float)
        df['ano_mes'] = df['data'].dt.to_period('M')
        return df.groupby('ano_mes')['valor'].mean().reset_index()
    except Exception as e:
        st.warning(f"Erro ao obter dados da série {codigo_serie} do BCB: {e}")
        return pd.DataFrame(columns=['ano_mes', 'valor'])

# --- Proteções para falhas em APIs externas ---
def proteger_dataframe(df, nome):
    if df.empty or 'valor' not in df:
        st.warning(f"⚠️ Indicador {nome} não disponível no momento. Será ignorado no gráfico.")
        return pd.DataFrame({'Mês': [], nome: []})
    df = df.rename(columns={'valor': nome, 'ano_mes': 'Mês'})
    df['Mês'] = df['Mês'].astype(str)
    return df

def obter_rentabilidade_fundo_cvm(cnpj_fundo, ano_mes_lista):
    cnpj_limpo = cnpj_fundo.replace('.', '').replace('/', '').replace('-', '')
    resultados = []
    for ano_mes in ano_mes_lista:
        ano, mes = ano_mes.split('-')
        url = f'https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ano}{mes}.zip'
        try:
            r = requests.get(url)
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                for file in z.namelist():
                    if file.endswith('.csv'):
                        df = pd.read_csv(z.open(file), sep=';', encoding='latin1')
                        df = df[df['CNPJ_FUNDO'] == cnpj_limpo]
                        df['DT_COMPTC'] = pd.to_datetime(df['DT_COMPTC'], format='%Y-%m-%d')
                        df = df.sort_values('DT_COMPTC')
                        df['VL_QUOTA'] = pd.to_numeric(df['VL_QUOTA'].str.replace(',', '.'), errors='coerce')
                        if not df.empty:
                            inicio = df.iloc[0]['VL_QUOTA']
                            fim = df.iloc[-1]['VL_QUOTA']
                            rentabilidade = ((fim / inicio) - 1) * 100
                            resultados.append({'mes': f"{ano}-{mes}", 'rentabilidade': rentabilidade})
        except Exception as e:
            st.error(f"Erro ao processar {ano_mes}: {e}")
    return resultados

def calcular_rentabilidade_liquida(dados_fundo, df_cdi, capital_inicial, retirada_mensal=0, aporte_mensal=0, reinvestir=True):
    resultados = []
    capital = capital_inicial

    for i in range(len(dados_fundo)):
        mes = dados_fundo[i]['mes']
        rent_bruta = dados_fundo[i]['rentabilidade']

        cdi_row = df_cdi[df_cdi['ano_mes'] == mes]
        if cdi_row.empty:
            continue
        cdi = cdi_row.iloc[0]['valor']

        excedente = max(0, rent_bruta - cdi)
        taxa_perf = excedente * 0.30
        rent_liquida = rent_bruta - cdi - taxa_perf
        rendimento_br = capital * (rent_liquida / 100)

        if reinvestir:
            capital += rendimento_br
        else:
            capital += max(0, rendimento_br - retirada_mensal)

        capital += aporte_mensal
        capital -= retirada_mensal

        resultados.append({
            'Mês': str(mes),
            'Rentabilidade Bruta (%)': rent_bruta,
            'CDI (%)': cdi,
            'Rentabilidade Líquida (%)': rent_liquida,
            'Rendimento Líquido (BRL)': rendimento_br,
            'Capital Final do Mês (BRL)': capital
        })

    return pd.DataFrame(resultados)

# --- Interface Streamlit ---
st.title("Calculadora de Rentabilidade Líquida - Fundo Transfero")

capital_investido = st.number_input("Capital inicial investido (BRL)", value=1_500_000, step=10000)
retirada_mensal = st.number_input("Retirada mensal desejada (BRL)", value=70000, step=1000)
aporte_mensal = st.number_input("Aporte mensal (BRL)", value=0, step=1000)
reinvestir = st.checkbox("Reinvestir rendimentos?", value=False)

data_fim_input = st.date_input("Data final da simulação", value=date.today(), min_value=date(2024, 7, 1), max_value=date.today())

st.markdown("---")

st.info("Baixando dados da CVM e indicadores BCB. Isso pode levar alguns segundos...")

data_inicio = '01/07/2024'
data_fim_str = data_fim_input.strftime('%d/%m/%Y')

df_cdi = obter_serie_bcb(4390, data_inicio, data_fim_str)
df_ibovespa = obter_serie_bcb(7, data_inicio, data_fim_str)
df_ipca = obter_serie_bcb(433, data_inicio, data_fim_str)
df_ifix = obter_serie_bcb(28501, data_inicio, data_fim_str)  # Supondo que esse seja o código correto

for df in [df_cdi, df_ibovespa, df_ipca, df_ifix]:
    df['ano_mes'] = df['ano_mes'].astype(str)

# Geração dinâmica das datas desejadas
data_inicio_obj = datetime.strptime("2024-07", "%Y-%m")
data_fim_obj = datetime(data_fim_input.year, data_fim_input.month, 1)
data_range = pd.date_range(start=data_inicio_obj, end=data_fim_obj, freq='MS')
datas_desejadas = [d.strftime("%Y-%m") for d in data_range]

dados_fundo = obter_rentabilidade_fundo_cvm("54.776.432/0001-18", datas_desejadas)

if not dados_fundo:
    st.error("Não foi possível obter os dados do fundo.")
else:
    df_resultado = calcular_rentabilidade_liquida(
        dados_fundo, df_cdi, capital_investido,
        retirada_mensal, aporte_mensal, reinvestir
    )

    st.success("Cálculo finalizado!")
    st.dataframe(df_resultado.style.format({
        "Rentabilidade Bruta (%)": "{:.2f}",
        "CDI (%)": "{:.2f}",
        "Rentabilidade Líquida (%)": "{:.2f}",
        "Rendimento Líquido (BRL)": "R$ {:,.2f}",
        "Capital Final do Mês (BRL)": "R$ {:,.2f}"
    }))

    st.markdown("### Evolução do Capital ao Longo do Tempo")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df_resultado['Mês'], df_resultado['Capital Final do Mês (BRL)'], marker='o')
    ax1.set_title("Evolução do Capital Final por Mês")
    ax1.set_xlabel("Mês")
    ax1.set_ylabel("Capital (R$)")
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)

    st.markdown("### Comparativo de Rentabilidade Mensal")
    df_resultado['Mês'] = pd.PeriodIndex(df_resultado['Mês'], freq='M').astype(str)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(df_resultado['Mês'], df_resultado['Rentabilidade Bruta (%)'], label='Fundo Transfero', marker='o')
    ax2.plot(df_resultado['Mês'], df_cdi['valor'], label='CDI', marker='x')
    ax2.plot(df_resultado['Mês'], df_ibovespa['valor'], label='IBOVESPA', marker='s')
    ax2.plot(df_resultado['Mês'], df_ipca['valor'], label='IPCA', marker='^')
    ax2.plot(df_resultado['Mês'], df_ifix['valor'], label='IFIX', marker='d')
    ax2.set_title("Rentabilidade Mensal: Fundo vs. Indicadores")
    ax2.set_xlabel("Mês")
    ax2.set_ylabel("Rentabilidade (%)")
    ax2.legend()
    ax2.grid(True)
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)
