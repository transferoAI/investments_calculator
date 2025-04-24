# 📈 Calculadora de Rentabilidade Líquida - Fundo Transfero

Este é um aplicativo interativo desenvolvido com [Streamlit](https://streamlit.io), que simula a rentabilidade líquida do fundo **Transfero Absolute Horizon FI** com base em dados oficiais da CVM e indicadores do Banco Central.

---

## ✅ Funcionalidades

- 💸 Simula rentabilidade líquida considerando:
  - 100% do CDI de administração
  - 30% de taxa de performance sobre o excedente do CDI
  - Retiradas mensais, aportes mensais e reinvestimentos

- 📊 Geração de gráficos:
  - Evolução do capital ao longo do tempo
  - Comparativo mensal com indicadores: **CDI, IBOVESPA, IPCA, IFIX**

- 📡 Dados dinâmicos via APIs públicas:
  - **CVM**: rentabilidade do fundo (por CNPJ)
  - **Banco Central do Brasil (SGS)**:
    - CDI (`4390`)
    - IBOVESPA (`7`)
    - IPCA (`433`)
    - IFIX (`28501`)

---

## 🚀 Como executar localmente

```bash
git clone https://github.com/seuusuario/seurepositorio.git
cd seurepositorio
pip install -r requirements.txt
streamlit run app.py
