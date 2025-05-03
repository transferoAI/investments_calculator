"""
Ponto de entrada do projeto de Calculadora de Investimentos.

Este módulo inicia o aplicativo principal.
"""

import os
import sys

# Adiciona o diretório src ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from web.app import MainApp

def main():
    """Função principal."""
    app = MainApp()
    app.render()

if __name__ == "__main__":
    main()
