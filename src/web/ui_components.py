"""
Componentes de interface do usuário.

Este módulo implementa os componentes de interface do usuário
usando Streamlit. O módulo é responsável por:

1. Renderizar o dashboard principal
2. Renderizar o formulário de entrada
3. Renderizar os resultados
4. Aplicar temas e estilos

Estrutura do módulo:
1. Classes de Componentes:
   - ThemeComponent: Gerencia temas e configurações
   - InputFormComponent: Gerencia formulário de entrada
   - DashboardComponent: Gerencia exibição de resultados
2. Funções Auxiliares:
   - formatar_moeda: Formatação de valores monetários
   - formatar_percentual: Formatação de percentuais
   - render_indicator_selector: Seleção de indicadores
   - render_results: Exibição de resultados detalhados

IMPORTANTE:
- Interface intuitiva e amigável
- Feedback visual claro
- Consistência no design
- Responsividade
- Documentação clara para facilitar manutenção
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, TypedDict, Union, Tuple
import plotly.express as px
import plotly.graph_objects as go
import locale
from dateutil.relativedelta import relativedelta
import os

from src.core.types import (
    SimulationParameters,
    SimulationResults,
    HistoricalSimulation,
    APIData,
    CalculationInput,
    CalculationOutput
)

from src.core.interfaces import IUIComponent
from src.core.exceptions import InvalidParameterError, ThemeError

from src.utils.logging import get_logger
from src.utils.export_utils import export_to_csv, export_to_excel, export_to_json

# Configuração inicial
logger = get_logger(__name__)

# Configuração do locale para formatação de valores
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        st.warning("Não foi possível configurar o locale para português do Brasil. Os valores monetários podem não ser exibidos corretamente.")

class ThemeComponent(IUIComponent):
    """
    Componente para gerenciamento de temas e configurações.
    
    Responsabilidades:
    1. Seleção e aplicação de temas
    2. Configurações de visualização
    3. Opções de exportação
    4. Configurações de alertas
    
    TODO:
    - Adicionar mais opções de temas
    - Implementar persistência de configurações
    - Adicionar suporte a temas personalizados
    """
    
    def __init__(self):
        """Inicializa o componente de tema."""
        self.css_file = os.path.join(os.path.dirname(__file__), 'styles.css')
        if not os.path.exists(self.css_file):
            raise ThemeError("Arquivo de estilos não encontrado")
    
    def render(self, data: Optional[Dict] = None) -> Tuple[str, bool, bool, bool, str]:
        """
        Renderiza o seletor de tema e aplica o tema selecionado.
        
        Args:
            data: Dados opcionais para configuração inicial
            
        Returns:
            Tuple contendo:
            - theme: Nome do tema selecionado
            - mostrar_tendencias: Flag para mostrar tendências
            - mostrar_estatisticas: Flag para mostrar estatísticas
            - mostrar_alertas: Flag para mostrar alertas
            - formato_exportacao: Formato de exportação selecionado
            
        Raises:
            ThemeError: Se houver erro ao aplicar o tema
        """
        try:
            # Carrega os estilos CSS
            with open(self.css_file, 'r') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            
            # Obtém as configurações do tema
            theme_config = self._render_theme_selector()
            
            # Aplica o tema
            self._apply_theme(theme_config[0])
            
            return theme_config
            
        except Exception as e:
            logger.error(f"Erro ao renderizar tema: {str(e)}")
            raise ThemeError(f"Erro ao renderizar tema: {str(e)}")
    
    def _render_theme_selector(self) -> Tuple[str, bool, bool, bool, str]:
        """
        Renderiza o seletor de tema e retorna as configurações.
        
        Returns:
            Tuple contendo as configurações do tema
            
        Raises:
            ThemeError: Se houver erro ao renderizar o seletor
        """
        try:
            with st.sidebar:
                st.title("⚙️ Configurações")
                
                # Seletor de tema
                theme = st.selectbox(
                    "🎨 Tema",
                    ["Claro", "Escuro"],
                    index=1,  # Escuro como padrão
                    help="Selecione o tema da interface"
                )
                
                # Configurações de visualização
                st.divider()
                st.subheader("📊 Visualização")
                mostrar_tendencias = st.checkbox(
                    "Mostrar tendências",
                    value=True,
                    help="Exibe as tendências dos indicadores no gráfico"
                )
                
                mostrar_estatisticas = st.checkbox(
                    "Mostrar estatísticas detalhadas",
                    value=True,
                    help="Exibe estatísticas adicionais dos resultados"
                )
                
                # Configurações de alertas
                st.divider()
                st.subheader("⚙️ Opções")
                mostrar_alertas = st.checkbox(
                    "Mostrar alertas",
                    value=True,
                    help="Exibe alertas sobre possíveis problemas nos cálculos"
                )
                
                # Configurações de exportação
                st.divider()
                st.subheader("💾 Exportação")
                formato_exportacao = st.selectbox(
                    "Formato de exportação",
                    ["Excel", "PDF", "CSV"],
                    index=0,
                    help="Selecione o formato para exportar os resultados"
                )
            
            return theme, mostrar_tendencias, mostrar_estatisticas, mostrar_alertas, formato_exportacao
            
        except Exception as e:
            logger.error(f"Erro ao renderizar seletor de tema: {str(e)}")
            raise ThemeError(f"Erro ao renderizar seletor de tema: {str(e)}")
    
    def _apply_theme(self, theme: str) -> None:
        """
        Aplica o tema selecionado.
        
        Args:
            theme: Nome do tema a ser aplicado
            
        Raises:
            ThemeError: Se houver erro ao aplicar o tema
        """
        try:
            # Define o atributo data-theme no body
            st.markdown(
                f'<body data-theme="{theme.lower()}">',
                unsafe_allow_html=True
            )
            
        except Exception as e:
            logger.error(f"Erro ao aplicar tema: {str(e)}")
            raise ThemeError(f"Erro ao aplicar tema: {str(e)}")

class InputFormComponent(IUIComponent):
    """
    Componente para formulário de entrada.
    
    Responsabilidades:
    1. Renderizar formulário de entrada
    2. Validar dados de entrada
    3. Retornar parâmetros validados
    4. Gerenciar seleção de indicadores
    """
    
    def __init__(self):
        """Inicializa o componente de formulário."""
        self.logger = get_logger(__name__)
    
    def render(self, data: Optional[Dict] = None) -> SimulationParameters:
        """
        Renderiza o formulário de entrada.
        
        Args:
            data: Dados opcionais para preenchimento inicial
            
        Returns:
            SimulationParameters: Parâmetros da simulação
            
        Raises:
            InvalidParameterError: Se os parâmetros forem inválidos
        """
        try:
            return self._render_form(data)
        except Exception as e:
            self.logger.error(f"Erro ao renderizar formulário: {str(e)}")
            st.error("Erro ao processar o formulário. Por favor, verifique os dados.")
            return None
    
    def _render_form(self, data: Optional[Dict] = None) -> SimulationParameters:
        """
        Renderiza o formulário e retorna os parâmetros.
        
        Args:
            data: Dados opcionais para preenchimento inicial
            
        Returns:
            SimulationParameters: Parâmetros da simulação
            
        Raises:
            InvalidParameterError: Se os parâmetros forem inválidos
        """
        st.title("💰 Calculadora de Investimentos")
        
        with st.form("investment_form"):
            # Capital inicial
            initial_capital = st.number_input(
                "Capital Inicial (R$)",
                min_value=0.0,
                value=10000.0,
                step=1000.0,
                format="%.2f",
                help="Valor inicial a ser investido"
            )
            
            # Aporte mensal
            monthly_contribution = st.number_input(
                "Aporte Mensal (R$)",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                format="%.2f",
                help="Valor a ser investido mensalmente"
            )
            
            # Retirada mensal
            monthly_withdrawal = st.number_input(
                "Retirada Mensal (R$)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                format="%.2f",
                help="Valor a ser retirado mensalmente"
            )
            
            # Taxa de inflação
            inflation_rate = st.number_input(
                "Taxa de Inflação Anual (%)",
                min_value=0.0,
                value=4.5,
                step=0.1,
                format="%.2f",
                help="Taxa de inflação anual esperada"
            ) / 100.0
            
            # Taxa livre de risco
            risk_free_rate = st.number_input(
                "Taxa Livre de Risco Anual (%)",
                min_value=0.0,
                value=6.5,
                step=0.1,
                format="%.2f",
                help="Taxa livre de risco anual (ex: Selic)"
            ) / 100.0
            
            # Datas
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Data Inicial",
                    value=datetime.now().date(),
                    help="Data de início da simulação"
                )
            with col2:
                end_date = st.date_input(
                    "Data Final",
                    value=(datetime.now() + relativedelta(years=5)).date(),
                    help="Data final da simulação"
                )
            
            # Indicadores
            indicators = self._render_indicator_selector(data)
            
            # Botão de submissão
            submitted = st.form_submit_button("Calcular")
            
            if submitted:
                # Validação dos parâmetros
                self._validate_parameters(
                    initial_capital,
                    monthly_contribution,
                    risk_free_rate,
                    (end_date - start_date).days // 30,
                    indicators
                )
                
                # Retorna os parâmetros validados
                return SimulationParameters(
                    initial_capital=initial_capital,
                    monthly_contribution=monthly_contribution,
                    monthly_withdrawal=monthly_withdrawal,
                    inflation_rate=inflation_rate,
                    risk_free_rate=risk_free_rate,
                    start_date=datetime.combine(start_date, datetime.min.time()),
                    end_date=datetime.combine(end_date, datetime.min.time()),
                    indicators=indicators
                )
            
            return None
    
    def _render_indicator_selector(self, data: Optional[Dict] = None) -> List[str]:
        """
        Renderiza o seletor de indicadores usando multiselect com nome completo.
        
        Args:
            data: Dados opcionais para seleção inicial
        
        Returns:
            List[str]: Lista de códigos dos indicadores selecionados
        """
        st.subheader("📊 Indicadores para Comparação")

        # Dicionário de indicadores com nome completo
        indicadores = {
            "SELIC": "Sistema Especial de Liquidação e de Custódia",
            "IPCA": "Índice Nacional de Preços ao Consumidor Amplo",
            "CDI": "Certificado de Depósito Interbancário",
            "IGPM": "Índice Geral de Preços do Mercado",
            "BVSP": "Ibovespa",
            "GSPC": "S&P 500",
            "BRL=X": "Dólar Comercial"            
        }
        # Opções para o multiselect
        indicator_options = [f"{codigo} - {nome}" for codigo, nome in indicadores.items()]
        # Mapeamento reverso para pegar o código a partir do label
        label_to_codigo = {f"{codigo} - {nome}": codigo for codigo, nome in indicadores.items()}

        # Seleção via multiselect
        selected_labels = st.multiselect(
            "Selecione os indicadores para comparação",
            options=indicator_options,
            default=[f"{codigo} - {nome}" for codigo, nome in indicadores.items() if codigo in (data or {}).get("indicators", [])],
            help="Escolha um ou mais indicadores para comparar"
        )
        # Retorna apenas os códigos selecionados
        return [label_to_codigo[label] for label in selected_labels]
    
    def _validate_parameters(
        self,
        initial_capital: float,
        monthly_contribution: float,
        risk_free_rate: float,
        period_months: int,
        indicators: List[str]
    ) -> None:
        """
        Valida os parâmetros de entrada.
        
        Args:
            initial_capital: Capital inicial
            monthly_contribution: Aporte mensal
            risk_free_rate: Taxa livre de risco
            period_months: Período em meses
            indicators: Lista de indicadores
            
        Raises:
            InvalidParameterError: Se algum parâmetro for inválido
        """
        if initial_capital <= 0:
            raise InvalidParameterError(
                "capital_inicial",
                "O capital inicial deve ser maior que zero"
            )
        
        if monthly_contribution < 0:
            raise InvalidParameterError(
                "aporte_mensal",
                "O aporte mensal não pode ser negativo"
            )
        
        if risk_free_rate < 0:
            raise InvalidParameterError(
                "taxa_juros",
                "A taxa de juros não pode ser negativa"
            )
        
        if period_months < 1:
            raise InvalidParameterError(
                "periodo",
                "O período deve ser de pelo menos 1 mês"
            )
        
        if not indicators:
            raise InvalidParameterError(
                "indicadores",
                "Selecione pelo menos um indicador para comparação"
            )

class DashboardComponent(IUIComponent):
    """
    Componente para gerenciamento do dashboard.
    
    Responsabilidades:
    1. Renderização do dashboard
    2. Exibição de métricas
    3. Visualização de gráficos
    4. Exportação de resultados
    
    TODO:
    - Adicionar mais tipos de visualização
    - Implementar filtros interativos
    - Adicionar suporte a múltiplos períodos
    """
    
    def __init__(self):
        """Inicializa o componente de dashboard."""
        self.css_file = os.path.join(os.path.dirname(__file__), 'styles.css')
        if not os.path.exists(self.css_file):
            raise ThemeError("Arquivo de estilos não encontrado")
    
    def render(self, data: Optional[Dict] = None) -> None:
        """
        Renderiza o dashboard com os resultados.
        
        Args:
            data: Dados para exibição no dashboard
            
        Raises:
            InvalidParameterError: Se houver erro na renderização
        """
        try:
            # Carrega os estilos CSS
            with open(self.css_file, 'r') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            
            # Renderiza o dashboard
            self._render_dashboard(data)
            
        except Exception as e:
            logger.error(f"Erro ao renderizar dashboard: {str(e)}")
            raise InvalidParameterError(f"Erro ao renderizar dashboard: {str(e)}")
    
    def _render_dashboard(self, data: Optional[Dict] = None) -> None:
        """
        Renderiza o dashboard com os resultados.
        
        Args:
            data: Dados para exibição no dashboard
            
        Raises:
            InvalidParameterError: Se houver erro na renderização
        """
        try:
            if not data:
                st.warning("Nenhum dado disponível para exibição")
                return
            
            # Título do dashboard
            st.title("📊 Resultados da Simulação")
            
            # Métricas principais
            self._render_metrics(data)
            
            # Gráficos
            self._render_charts(data)
            
            # Análise de risco
            self._render_risk_analysis(data)
            
            # Opções de exportação
            self._render_export_options(data)
            
        except Exception as e:
            logger.error(f"Erro ao renderizar dashboard: {str(e)}")
            raise InvalidParameterError(f"Erro ao renderizar dashboard: {str(e)}")
    
    def _render_metrics(self, data: Dict) -> None:
        """
        Renderiza as métricas principais.
        
        Args:
            data: Dados para exibição das métricas
            
        Raises:
            InvalidParameterError: Se houver erro na renderização
        """
        try:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "💰 Valor Final",
                    formatar_moeda(data.get('valor_final', 0)),
                    help="Valor total ao final do período"
                )
            
            with col2:
                st.metric(
                    "📈 Retorno Total",
                    formatar_percentual(data.get('retorno_total', 0)),
                    help="Retorno total do investimento"
                )
            
            with col3:
                st.metric(
                    "💵 Aporte Total",
                    formatar_moeda(data.get('aporte_total', 0)),
                    help="Total de aportes realizados"
                )
            
        except Exception as e:
            logger.error(f"Erro ao renderizar métricas: {str(e)}")
            raise InvalidParameterError(f"Erro ao renderizar métricas: {str(e)}")
    
    def _render_charts(self, data: Dict) -> None:
        """
        Renderiza os gráficos.
        
        Args:
            data: Dados para exibição dos gráficos
            
        Raises:
            InvalidParameterError: Se houver erro na renderização
        """
        try:
            # Gráfico de evolução
            st.subheader("📈 Evolução do Investimento")
            fig = px.line(
                data.get('evolucao', pd.DataFrame()),
                x='data',
                y='valor',
                title='Evolução do Valor do Investimento',
                labels={'data': 'Data', 'valor': 'Valor (R$)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de composição
            st.subheader("📊 Composição do Investimento")
            fig = px.pie(
                data.get('composicao', pd.DataFrame()),
                values='valor',
                names='tipo',
                title='Composição do Investimento',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Erro ao renderizar gráficos: {str(e)}")
            raise InvalidParameterError(f"Erro ao renderizar gráficos: {str(e)}")
    
    def _render_risk_analysis(self, data: Dict) -> None:
        """
        Renderiza a análise de risco.
        
        Args:
            data: Dados para exibição da análise de risco
            
        Raises:
            InvalidParameterError: Se houver erro na renderização
        """
        try:
            st.subheader("⚠️ Análise de Risco")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "📊 Volatilidade",
                    formatar_percentual(data.get('volatilidade', 0)),
                    help="Volatilidade do investimento"
                )
            
            with col2:
                st.metric(
                    "📈 Sharpe Ratio",
                    f"{data.get('sharpe_ratio', 0):.2f}",
                    help="Índice de Sharpe"
                )
            
            # Gráfico de distribuição de retornos
            fig = px.histogram(
                data.get('retornos', pd.DataFrame()),
                x='retorno',
                title='Distribuição de Retornos',
                labels={'retorno': 'Retorno (%)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Erro ao renderizar análise de risco: {str(e)}")
            raise InvalidParameterError(f"Erro ao renderizar análise de risco: {str(e)}")
    
    def _render_export_options(self, data: Dict) -> None:
        """
        Renderiza as opções de exportação.
        
        Args:
            data: Dados para exportação
            
        Raises:
            InvalidParameterError: Se houver erro na renderização
        """
        try:
            st.subheader("💾 Exportar Resultados")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Exportar para CSV"):
                    export_to_csv(data)
                    st.success("Dados exportados com sucesso!")
            
            with col2:
                if st.button("📊 Exportar para Excel"):
                    export_to_excel(data)
                    st.success("Dados exportados com sucesso!")
            
            with col3:
                if st.button("📋 Exportar para JSON"):
                    export_to_json(data)
                    st.success("Dados exportados com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao renderizar opções de exportação: {str(e)}")
            raise InvalidParameterError(f"Erro ao renderizar opções de exportação: {str(e)}")

# Funções auxiliares
def formatar_moeda(valor):
    """Formata um valor numérico como moeda brasileira (R$)."""
    try:
        return locale.currency(valor, grouping=True, symbol=True)
    except:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_percentual(valor):
    """Formata um valor numérico como percentual."""
    try:
        return f"{valor:.2f}%"
    except:
        return f"{valor}%"

def render_indicator_selector(indicadores_disponiveis):
    """Renderiza o seletor de indicadores e retorna os indicadores selecionados."""
    st.subheader("📊 Seletor de Indicadores")
    
    with st.expander("🔍 Indicadores BCB", expanded=True):
        indicadores_bcb = st.multiselect(
            "🔍 Selecione os indicadores do BCB",
            options=list(indicadores_disponiveis['bcb'].keys()),
            default=["CDI", "Selic"],
            help="Indicadores do Banco Central do Brasil"
        )
    
    with st.expander("📊 Indicadores YFinance", expanded=True):
        indicadores_yfinance = st.multiselect(
            "📊 Selecione os indicadores do YFinance",
            options=list(indicadores_disponiveis['yfinance'].keys()),
            default=["IBOVESPA", "S&P 500"],
            help="Indicadores do Yahoo Finance"
        )
    
    with st.expander("📈 Indicadores Personalizados", expanded=False):
        st.subheader("📊 Adicionar Indicador Personalizado")
        novo_indicador = st.text_input(
            "📝 Nome do Indicador",
            help="Nome para o indicador personalizado"
        )
        
        if novo_indicador:
            valor_inicial = st.number_input(
                "💰 Valor Inicial",
                min_value=0.0,
                value=100.0,
                step=0.1,
                format="%.2f",
                help="Valor inicial do indicador"
            )
            
            taxa_retorno = st.number_input(
                "📈 Taxa de Retorno Mensal",
                min_value=0.0,
                max_value=100.0,
                value=1.0,
                step=0.1,
                format="%.1f",
                help="Taxa de retorno mensal em porcentagem"
            )
            
            if st.button("➕ Adicionar Indicador"):
                indicadores_disponiveis['personalizado'][novo_indicador] = {
                    'valor_inicial': valor_inicial,
                    'taxa_retorno': taxa_retorno
                }
                st.success(f"Indicador '{novo_indicador}' adicionado com sucesso!")
    
    # Combinando os indicadores selecionados
    indicadores_selecionados = []
    for nome in indicadores_bcb:
        indicadores_selecionados.append((nome, 'bcb'))
    for nome in indicadores_yfinance:
        indicadores_selecionados.append((nome, 'yfinance'))
    
    # Botão de cálculo com loading
    with st.spinner("Calculando..."):
        calcular = st.button(
            "🚀 Calcular Rentabilidade",
            type="primary",
            help="Inicia o cálculo da rentabilidade"
        )
    
    return indicadores_selecionados, calcular

def render_results(df_resultado, dados_indicadores, indicadores_selecionados, mostrar_tendencias, mostrar_estatisticas):
    """Renderiza os resultados da simulação."""
    st.subheader("📊 Resultados da Simulação")
    
    # Exibindo o gráfico principal
    st.markdown("### 📈 Evolução do Capital e Indicadores")
    
    # Criando figura com subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    
    # Gráfico principal de evolução do capital
    ax1.plot(df_resultado.index, df_resultado['Saldo'], label='Capital', color='#2563eb', linewidth=2)
    
    # Adicionando indicadores selecionados
    for nome, tipo in indicadores_selecionados:
        if tipo == 'bcb':
            if nome in dados_indicadores:
                ax1.plot(
                    dados_indicadores[nome].index,
                    dados_indicadores[nome]['valor'],
                    label=nome,
                    linestyle='--',
                    alpha=0.7
                )
        elif tipo == 'yfinance':
            simbolo = dados_indicadores.get(nome)
            if simbolo is not None and simbolo in dados_indicadores:
                ax1.plot(
                    dados_indicadores[simbolo].index,
                    dados_indicadores[simbolo]['retorno'],
                    label=nome,
                    linestyle='--',
                    alpha=0.7
                )
    
    ax1.set_title("Evolução do Capital e Indicadores")
    ax1.set_ylabel("Valor (R$)")
    ax1.grid(True)
    ax1.legend()
    
    # Gráfico secundário de rentabilidade mensal
    if mostrar_tendencias:
        ax2.plot(
            df_resultado.index,
            df_resultado['Saldo'].pct_change() * 100,
            label='Rentabilidade Mensal',
            color='#16a34a',
            linewidth=2
        )
        ax2.set_title("Rentabilidade Mensal")
        ax2.set_ylabel("Rentabilidade (%)")
        ax2.grid(True)
    
    st.pyplot(fig)
    
    # Exibindo estatísticas principais
    st.markdown("### 📊 Estatísticas Principais")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Capital Final",
            formatar_moeda(df_resultado['Saldo'].iloc[-1]),
            delta=formatar_moeda(df_resultado['Saldo'].iloc[-1] - df_resultado['Capital'].iloc[0])
        )
    
    with col2:
        rentabilidade_total = (df_resultado['Saldo'].iloc[-1] / df_resultado['Capital'].iloc[0] - 1) * 100
        st.metric(
            "📈 Rentabilidade Total",
            formatar_percentual(rentabilidade_total),
            delta=formatar_percentual(rentabilidade_total - 100)
        )
    
    with col3:
        volatilidade = df_resultado['Saldo'].pct_change().std() * 100
        st.metric(
            "📊 Volatilidade",
            formatar_percentual(volatilidade)
        )
    
    with col4:
        sharpe_ratio = (rentabilidade_total - 2.25) / volatilidade
        st.metric(
            "⭐️ Índice de Sharpe",
            f"{sharpe_ratio:.2f}"
        )
    
    # Exibindo estatísticas detalhadas
    if mostrar_estatisticas:
        st.markdown("### 📊 Estatísticas Detalhadas")
        
        # Criando DataFrame com estatísticas
        estatisticas = {
            "Métrica": [
                "Média Mensal",
                "Média Anual",
                "Máximo",
                "Mínimo",
                "Desvio Padrão",
                "Coeficiente de Variação"
            ],
            "Valor": [
                formatar_moeda(df_resultado['Saldo'].mean()),
                formatar_moeda(df_resultado['Saldo'].mean() * 12),
                formatar_moeda(df_resultado['Saldo'].max()),
                formatar_moeda(df_resultado['Saldo'].min()),
                formatar_moeda(df_resultado['Saldo'].std()),
                f"{df_resultado['Saldo'].std() / df_resultado['Saldo'].mean():.2%}"
            ]
        }
        
        df_estatisticas = pd.DataFrame(estatisticas)
        st.dataframe(df_estatisticas, use_container_width=True)
    
    # Adicionando recomendações
    st.markdown("### 📝 Recomendações")
    
    # Analisando rentabilidade
    if rentabilidade_total > 100:
        st.success("✅ Excelente rentabilidade! Seu investimento está performando muito bem.")
    elif rentabilidade_total > 50:
        st.info("ℹ️ Boa rentabilidade! Seu investimento está performando bem.")
    else:
        st.warning("⚠️ Rendimento abaixo do esperado. Considere revisar sua estratégia de investimento.")
    
    # Analisando volatilidade
    if volatilidade < 10:
        st.success("✅ Baixa volatilidade! Seu portfólio é estável.")
    elif volatilidade < 20:
        st.info("ℹ️ Volatilidade moderada. Seu portfólio tem alguns riscos.")
    else:
        st.warning("⚠️ Alta volatilidade! Seu portfólio tem riscos significativos.")
    
    # Adicionando botões de ação
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Recalcular com Novos Parâmetros"):
            st.experimental_rerun()
    
    with col2:
        if st.button("💾 Exportar Resultados"):
            st.success("Resultados exportados com sucesso!")
    
    # Exibindo a tabela de resultados
    st.dataframe(
        df_resultado.style.format({
            'Capital': formatar_moeda,
            'Retirada': formatar_moeda,
            'Aporte': formatar_moeda,
            'Saldo': formatar_moeda,
            'Rentabilidade': formatar_percentual
        }),
        use_container_width=True
    )

def render_dashboard(df_resultado, dados_indicadores, indicadores_selecionados):
    """Renderiza o dashboard com cards informativos e gráficos interativos."""
    st.title("📊 Dashboard de Análise")
    
    # Cards com métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Capital Final",
            formatar_moeda(df_resultado['Saldo'].iloc[-1]),
            delta=formatar_moeda(df_resultado['Saldo'].iloc[-1] - df_resultado['Capital'].iloc[0])
        )
    
    with col2:
        rentabilidade_total = ((df_resultado['Saldo'].iloc[-1] / df_resultado['Capital'].iloc[0]) - 1) * 100
        st.metric(
            "Rentabilidade Total",
            formatar_percentual(rentabilidade_total),
            delta=formatar_percentual(df_resultado['Rentabilidade'].mean())
        )
    
    with col3:
        volatilidade = df_resultado['Rentabilidade'].std()
        st.metric(
            "Volatilidade",
            formatar_percentual(volatilidade),
            delta=formatar_percentual(volatilidade - df_resultado['Rentabilidade'].std())
        )
    
    with col4:
        indice_sharpe = (rentabilidade_total - 0.0225) / volatilidade if volatilidade != 0 else 0
        st.metric(
            "Índice de Sharpe",
            f"{indice_sharpe:.2f}",
            delta=f"{indice_sharpe - 1:.2f}"
        )
    
    # Gráfico de evolução do patrimônio
    st.subheader("📈 Evolução do Patrimônio")
    fig = px.line(
        df_resultado,
        x=df_resultado.index,
        y=['Saldo', 'Capital'],
        title='Evolução do Patrimônio ao Longo do Tempo',
        labels={'value': 'Valor (R$)', 'variable': 'Tipo'},
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de rentabilidade mensal
    st.subheader("📊 Rentabilidade Mensal")
    fig = px.bar(
        df_resultado,
        x=df_resultado.index,
        y='Rentabilidade',
        title='Rentabilidade Mensal',
        labels={'Rentabilidade': 'Rentabilidade (%)'},
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparação com indicadores
    st.subheader("🔍 Comparação com Indicadores")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Indicadores Selecionados:**")
        for indicador in indicadores_selecionados:
            st.write(f"- {indicador[0]}")
    
    with col2:
        st.write("**Dados dos Indicadores:**")
        for nome, dados in dados_indicadores.items():
            if 'valor' in dados.columns:
                st.write(f"- {nome}: {dados['valor'].iloc[-1]:.2f}")
            elif 'retorno' in dados.columns:
                st.write(f"- {nome}: {dados['retorno'].iloc[-1]:.2f}%")
    
    # Análise de Risco
    st.subheader("⚠️ Análise de Risco")
    risco = "Baixo" if volatilidade < 5 else "Médio" if volatilidade < 10 else "Alto"
    st.info(f"""
        - **Nível de Risco**: {risco}
        - **Volatilidade**: {formatar_percentual(volatilidade)}
        - **Índice de Sharpe**: {indice_sharpe:.2f}
        - **Rentabilidade Média**: {formatar_percentual(df_resultado['Rentabilidade'].mean())}
    """)
    
    # Recomendações
    st.subheader("💡 Recomendações")
    if indice_sharpe > 1:
        st.success("O investimento apresenta um bom retorno ajustado ao risco.")
    elif indice_sharpe > 0:
        st.warning("O investimento apresenta retorno positivo, mas poderia ser melhor ajustado ao risco.")
    else:
        st.error("O investimento não está compensando adequadamente o risco assumido.")

def render_input_form() -> Dict:
    """
    Renderiza o formulário de entrada.
    
    Esta função renderiza o formulário para entrada
    dos parâmetros da simulação.
    
    Returns:
        Dict: Dicionário com os parâmetros inseridos
        
    Exemplo:
        params = render_input_form()
    """
    
    try:
        # Seção de parâmetros básicos
        st.header("📝 Parâmetros da Simulação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            initial_capital = st.number_input(
                "Capital Inicial (R$)",
                min_value=0.0,
                value=10000.0,
                step=1000.0
            )
            
            monthly_contribution = st.number_input(
                "Aporte Mensal (R$)",
                min_value=0.0,
                value=1000.0,
                step=100.0
            )
            
            monthly_withdrawal = st.number_input(
                "Retirada Mensal (R$)",
                min_value=0.0,
                value=0.0,
                step=100.0
            )
        
        with col2:
            inflation_rate = st.number_input(
                "Taxa de Inflação (% a.a.)",
                min_value=0.0,
                value=5.0,
                step=0.1
            ) / 100
            
            risk_free_rate = st.number_input(
                "Taxa Livre de Risco (% a.a.)",
                min_value=0.0,
                value=10.0,
                step=0.1
            ) / 100
            
            months = st.number_input(
                "Período (meses)",
                min_value=1,
                value=12,
                step=1
            )
        
        # Cálculo das datas
        start_date = datetime.now()
        end_date = start_date + relativedelta(months=months)
        
        # Botão para calcular
        if st.button("Calcular"):
            return {
                "initial_capital": initial_capital,
                "monthly_contribution": monthly_contribution,
                "monthly_withdrawal": monthly_withdrawal,
                "inflation_rate": inflation_rate,
                "risk_free_rate": risk_free_rate,
                "start_date": start_date,
                "end_date": end_date
            }
        
        return {}
        
    except Exception as e:
        st.error(f"Erro ao renderizar formulário: {str(e)}")
        return {} 