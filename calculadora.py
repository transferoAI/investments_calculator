import pandas as pd

def calcular_rentabilidade_liquida(dados_fundo, df_cdi, capital_inicial, retirada_mensal=0, aporte_mensal=0, reinvestir=True):
    """
    Calcula a rentabilidade líquida de um investimento considerando CDI, taxas e aportes/retiradas.
    
    Args:
        dados_fundo (list): Lista de dicionários com dados de rentabilidade do fundo
        df_cdi (pd.DataFrame): DataFrame com dados do CDI
        capital_inicial (float): Capital inicial investido
        retirada_mensal (float): Valor mensal a ser retirado
        aporte_mensal (float): Valor mensal a ser aportado
        reinvestir (bool): Se True, reinveste os rendimentos
        
    Returns:
        pd.DataFrame: DataFrame com os resultados do cálculo
    """
    resultados = []
    capital = capital_inicial

    for i in range(len(dados_fundo)):
        mes = dados_fundo[i]['mes']
        rent_bruta = dados_fundo[i]['rentabilidade']

        # Obtém o CDI do mês
        cdi_row = df_cdi[df_cdi['ano_mes'] == mes]
        if cdi_row.empty:
            continue
        cdi = cdi_row.iloc[0]['valor']

        # Calcula a rentabilidade líquida
        excedente = max(0, rent_bruta - cdi)
        taxa_perf = excedente * 0.30
        rent_liquida = rent_bruta - cdi - taxa_perf
        rendimento_br = capital * (rent_liquida / 100)

        # Atualiza o capital
        if reinvestir:
            capital += rendimento_br
        else:
            capital += max(0, rendimento_br - retirada_mensal)

        capital += aporte_mensal
        capital -= retirada_mensal

        # Adiciona o resultado do mês
        resultados.append({
            'Mês': str(mes),
            'Rentabilidade Bruta (%)': rent_bruta,
            'CDI (%)': cdi,
            'Rentabilidade Líquida (%)': rent_liquida,
            'Rendimento Líquido (BRL)': rendimento_br,
            'Capital Final do Mês (BRL)': capital
        })

    return pd.DataFrame(resultados) 