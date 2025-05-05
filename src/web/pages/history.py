"""
Módulo da página de histórico.

Este módulo contém a lógica e interface da página de histórico de simulações.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def render_history_page():
    """Renderiza a página de histórico."""
    st.header("Histórico de Simulações")
    
    # Obtém o histórico do estado da sessão
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
        
        # Exibe o DataFrame
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