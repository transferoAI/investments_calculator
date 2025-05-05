"""
Módulo da página de dados do fundo.

Este módulo contém a lógica e interface da página de dados do fundo de investimento.
"""

import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

from src.services.cvm_api import CVMDataFetcher
from src.core.exceptions import APIError
from constants import FUNDO_CNPJ

def render_fund_data_page():
    """Renderiza a página de dados do fundo."""
    st.header("Rentabilidade do Fundo")
    
    # Select box para escolher a visualização
    view_options = {
        "Diária": "D",
        "Mensal": "M",
        "Semestral": "S",
        "Anual": "A"
    }
    selected_view = st.selectbox(
        "Visualização",
        options=list(view_options.keys()),
        index=0,
        help="Selecione a periodicidade dos dados a serem exibidos"
    )
    
    # Inicializa o fetcher
    cvm_fetcher = CVMDataFetcher()
    
    # Remove formatação do CNPJ
    cnpj_clean = FUNDO_CNPJ.replace(".", "").replace("/", "").replace("-", "")
    
    # Seção de atualização de dados
    st.subheader("Atualização de Dados")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Atualizar Dados do Fundo", key="update_fund_data"):
            # Verifica se já existem dados no banco
            ultima_data = cvm_fetcher.db_manager.get_last_date_for_fund(cnpj_clean)
            data_atual = datetime.now()
            
            if ultima_data and (data_atual - ultima_data).days < 1:
                st.info("Os dados já estão atualizados no banco de dados.")
            else:
                # Inicia o processo de atualização
                cvm_fetcher.fetch_data([cnpj_clean], data_atual)
    
    # Exibe o status do download/processamento
    status = cvm_fetcher.get_status()
    if status["is_running"]:
        st.info(f"Status: {status['status']}")
        st.progress(status["progress"] / 100)
        st.write(f"Processado: {status['processed_months']} de {status['total_months']} meses")
    elif status["status"]:
        st.success(status["status"])
    
    # Seção de visualização de dados
    st.subheader("Visualização de Dados")
    
    # Obtém os dados do fundo do banco
    fund_data = cvm_fetcher.db_manager.get_fund_data(cnpj_clean)
    
    if not fund_data.empty:
        # Filtra os dados de acordo com a visualização selecionada
        filtered_data = fund_data[fund_data["TIPO_QUOTA"] == view_options[selected_view]]
        
        if not filtered_data.empty:
            # Exibe os dados em uma tabela
            st.dataframe(
                filtered_data,
                use_container_width=True,
                hide_index=True
            )
            
            # Cria um gráfico de linha com Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=filtered_data["DT_COMPTC"],
                y=filtered_data["VL_QUOTA"],
                mode="lines",
                name="Valor da Cota",
                hovertemplate="Data: %{x}<br>Valor: R$ %{y:.2f}<extra></extra>"
            ))
            
            fig.update_layout(
                title="Evolução do Valor da Cota",
                xaxis_title="Data",
                yaxis_title="Valor da Cota (R$)",
                hovermode="x unified",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Botão para exportar dados
            csv_data = filtered_data.to_csv(
                index=False,
                sep=',',
                decimal='.',
                encoding='utf-8',
                date_format='%Y-%m-%d'
            ).encode('utf-8')
            
            st.download_button(
                label="Exportar Dados (CSV)",
                data=csv_data,
                file_name=f"dados_fundo_{cnpj_clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"Nenhum dado encontrado para a visualização {selected_view}")
    else:
        st.warning("Nenhum dado disponível para o fundo selecionado.") 