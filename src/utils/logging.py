"""
Utilitários de logging para o projeto de Calculadora de Investimentos.

Este módulo configura e fornece funções de logging.
"""

import logging
from typing import Optional
from pathlib import Path

# Configuração básica do logging
def setup_logging(
    name: str,
    level: int = logging.INFO,
    file_path: Optional[str] = None
) -> logging.Logger:
    """
    Configura e retorna um logger.
    
    Args:
        name (str): Nome do logger
        level (int): Nível de logging
        file_path (Optional[str]): Caminho para arquivo de log
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Criar diretório para logs se não existir
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Formato dos logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo, se fornecido
    if file_path:
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Logger para o projeto
project_logger = setup_logging("investments_calculator", file_path="logs/investments_calculator.log")
