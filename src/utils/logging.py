"""
Configuração de logging para o projeto.

Este módulo implementa a configuração centralizada de logging
para todo o projeto. O módulo é responsável por:

1. Configurar o formato dos logs
2. Configurar os níveis de log
3. Configurar os handlers de log
4. Fornecer uma interface para obtenção de loggers

IMPORTANTE:
- Logs devem ser informativos e úteis
- Níveis de log apropriados para cada situação
- Formato consistente em todo o projeto
- Tratamento adequado de erros
"""

import logging
import sys
from typing import Optional, Dict, List, TypedDict, Union, Any, Callable
from pathlib import Path

# Configuração do formato dos logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configuração dos níveis de log
LOG_LEVEL = logging.INFO

# Configuração do diretório de logs
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"

# Logger principal do projeto
project_logger = None

def setup_logging() -> None:
    """
    Configura o logging do projeto.
    
    Esta função configura o logging centralizado do projeto,
    incluindo formato, níveis e handlers.
    
    Exemplo:
        setup_logging()
        logger = get_logger(__name__)
        logger.info("Mensagem de log")
    """
    
    try:
        # Cria o diretório de logs se não existir
        LOG_DIR.mkdir(exist_ok=True)
        
        # Configura o logger raiz
        root_logger = logging.getLogger()
        root_logger.setLevel(LOG_LEVEL)
        
        # Remove handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Configura o handler para arquivo
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(
            logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        )
        root_logger.addHandler(file_handler)
        
        # Configura o handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        )
        root_logger.addHandler(console_handler)
        
        # Configura o logger principal do projeto
        global project_logger
        project_logger = get_logger("project")
        
    except Exception as e:
        print(f"Erro ao configurar logging: {str(e)}")
        sys.exit(1)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obtém um logger configurado.
    
    Esta função retorna um logger configurado com as
    configurações padrão do projeto.
    
    Args:
        name (Optional[str]): Nome do logger
        
    Returns:
        logging.Logger: Logger configurado
        
    Exemplo:
        logger = get_logger(__name__)
        logger.info("Mensagem de log")
    """
    
    try:
        # Configura o logging se ainda não estiver configurado
        if not logging.getLogger().handlers:
            setup_logging()
        
        # Retorna o logger
        return logging.getLogger(name)
        
    except Exception as e:
        print(f"Erro ao obter logger: {str(e)}")
        return logging.getLogger(name)

# Configura o logging ao importar o módulo
setup_logging()
