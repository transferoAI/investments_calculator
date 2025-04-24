# 📈 Calculadora de Rentabilidade Líquida - Fundo Transfero

Este é um aplicativo interativo desenvolvido com [Streamlit](https://streamlit.io) que calcula e analisa a rentabilidade do fundo de investimento com CNPJ 54.776.432/0001-18, utilizando dados oficiais da CVM (Comissão de Valores Mobiliários) e indicadores do mercado financeiro.

## 🎯 Objetivo

Fornecer uma ferramenta de análise e simulação para o fundo, permitindo que usuários possam:
- Visualizar a rentabilidade histórica desde julho de 2024
- Comparar o desempenho com diferentes indicadores
- Simular cenários de investimento com aportes e retiradas

## ✨ Funcionalidades

- 📊 **Análise de Rentabilidade**
  - Dados oficiais da CVM
  - Período de análise flexível (a partir de julho/2024)
  - Cálculo de rentabilidade mensal

- 💰 **Simulação de Investimentos**
  - Capital inicial customizável
  - Aportes mensais
  - Retiradas mensais
  - Opção de reinvestimento

- 📈 **Indicadores Comparativos**
  - BCB (Banco Central do Brasil):
    - CDI
    - Selic
    - IPCA
    - IGP-M
    - Poupança
  - Yahoo Finance:
    - IBOVESPA
    - S&P 500
    - Dólar
    - Ouro

- 📋 **Relatórios e Exportação**
  - Visualização de resultados em tabelas e gráficos
  - Exportação de dados para CSV
  - Relatórios detalhados de performance

## 🚀 Como Executar

1. **Pré-requisitos**
   ```bash
   # Python 3.8 ou superior
   python --version
   ```

2. **Instalação**
   ```bash
   # Clone o repositório
   git clone https://github.com/seu-usuario/investments_calculator.git
   cd investments_calculator

   # Instale as dependências
   pip install -r requirements.txt
   ```

3. **Execução**
   ```bash
   streamlit run app.py
   ```

## 🔧 Configuração

O sistema utiliza as seguintes configurações padrão:
- CNPJ do fundo: 54.776.432/0001-18
- Data inicial disponível: Julho de 2024
- Moedas suportadas: BRL (R$) e USD ($)
- Idiomas disponíveis: Português e Inglês

## 📚 Estrutura do Projeto

```bash
git clone https://github.com/seuusuario/seurepositorio.git
cd seurepositorio
pip install -r requirements.txt
streamlit run app.py
