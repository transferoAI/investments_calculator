# Calculadora de Investimentos

Uma calculadora interativa para simular investimentos com diferentes parâmetros, seguindo os padrões de arquitetura Python.

## Funcionalidades

- Simulação de investimentos com capital inicial, aportes mensais e retiradas
- Cálculo de rentabilidade total e volatilidade
- Índice de Sharpe para avaliação do risco
- Exportação de resultados em diferentes formatos
- Histórico de simulações
- Interface web interativa

## Arquitetura

O projeto segue os seguintes princípios:

- **SOLID**: Separação de responsabilidades através de interfaces e classes
- **PEP 8**: Segue as convenções de estilo do Python
- **Clean Architecture**: Organização em camadas (core, data, services, utils, web)
- **Type Hints**: Uso extensivo de anotações de tipo para melhor manutenibilidade
- **Logging**: Sistema de logging estruturado
- **Testing**: Suporte para testes unitários e de integração

## Requisitos

- Python 3.9+
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/transferoAI/investments_calculator.git
cd investments_calculator
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o pre-commit:
```bash
pre-commit install
```

5. Execute o aplicativo:
```bash
streamlit run app.py
```

## Desenvolvimento

### Estrutura do Projeto

```
investments_calculator/
├── src/
│   ├── core/           # Lógica de negócio
│   ├── data/           # Persistência de dados
│   ├── services/       # Serviços e orquestração
│   ├── utils/          # Utilitários
│   └── web/            # Interface web
├── tests/              # Testes unitários e de integração
├── docs/               # Documentação
├── .pre-commit-config.yaml  # Configuração do pre-commit
├── requirements.txt     # Dependências do projeto
└── README.md           # Documentação do projeto
```

### Padrões de Código

- **Nomenclatura**: snake_case para funções e variáveis, PascalCase para classes
- **Docstrings**: Uso de docstrings para todas as funções e classes
- **Type Hints**: Anotações de tipo obrigatórias
- **Logging**: Uso consistente do sistema de logging
- **Testing**: Cobertura mínima de 80% nos testes

## Uso

1. Preencha os campos do formulário com os parâmetros desejados
2. Selecione os indicadores para análise
3. Clique em "Calcular" para ver os resultados
4. Use os botões de exportação para salvar os resultados
5. Acesse o histórico de simulações através do menu

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
