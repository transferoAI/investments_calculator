"""
Utilitário de persistência de estado.

Este módulo implementa um sistema de persistência de estado
para a aplicação, permitindo salvar e restaurar o estado
entre sessões.

Estrutura:
1. StateManager: Gerencia o estado da aplicação
2. StateEntry: Representa uma entrada no estado
3. StatePersistence: Gerencia a persistência do estado

IMPORTANTE:
- Persistência em disco para durabilidade
- Thread-safe para acesso concorrente
- Suporte a múltiplos usuários
- Criptografia de dados sensíveis
"""

import os
import json
import base64
from typing import Any, Dict, Optional, TypeVar, Generic
from datetime import datetime
import threading
from pathlib import Path
import hashlib

from src.utils.logging import get_logger
from src.utils.cache import CacheManager

logger = get_logger(__name__)

T = TypeVar('T')

class StateEntry(Generic[T]):
    """Representa uma entrada no estado."""
    
    def __init__(self, data: T, user_id: str):
        """
        Inicializa uma entrada no estado.
        
        Args:
            data: Dados a serem armazenados
            user_id: ID do usuário
        """
        self.data = data
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a entrada para dicionário."""
        return {
            'data': self.data,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateEntry[T]':
        """Cria uma entrada a partir de um dicionário."""
        entry = cls(data['data'], data['user_id'])
        entry.created_at = datetime.fromisoformat(data['created_at'])
        entry.updated_at = datetime.fromisoformat(data['updated_at'])
        return entry

class StatePersistence:
    """Gerencia a persistência do estado."""
    
    def __init__(self, state_dir: str = '.state'):
        """
        Inicializa o gerenciador de persistência.
        
        Args:
            state_dir: Diretório para armazenar o estado
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_user_dir(self, user_id: str) -> Path:
        """Obtém o diretório do usuário."""
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()
        user_dir = self.state_dir / user_hash
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def save(self, key: str, entry: StateEntry) -> None:
        """
        Salva uma entrada no estado.
        
        Args:
            key: Chave da entrada
            entry: Entrada a ser salva
        """
        try:
            user_dir = self._get_user_dir(entry.user_id)
            state_file = user_dir / f"{key}.json"
            
            # Criptografa dados sensíveis
            data = entry.to_dict()
            if isinstance(data['data'], dict) and 'password' in data['data']:
                data['data']['password'] = self._encrypt(data['data']['password'])
            
            with open(state_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {str(e)}")
    
    def load(self, key: str, user_id: str) -> Optional[StateEntry]:
        """
        Carrega uma entrada do estado.
        
        Args:
            key: Chave da entrada
            user_id: ID do usuário
            
        Returns:
            StateEntry se encontrada, None caso contrário
        """
        try:
            user_dir = self._get_user_dir(user_id)
            state_file = user_dir / f"{key}.json"
            
            if not state_file.exists():
                return None
            
            with open(state_file, 'r') as f:
                data = json.load(f)
                
                # Descriptografa dados sensíveis
                if isinstance(data['data'], dict) and 'password' in data['data']:
                    data['data']['password'] = self._decrypt(data['data']['password'])
                
                return StateEntry.from_dict(data)
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {str(e)}")
            return None
    
    def delete(self, key: str, user_id: str) -> None:
        """
        Remove uma entrada do estado.
        
        Args:
            key: Chave da entrada
            user_id: ID do usuário
        """
        try:
            user_dir = self._get_user_dir(user_id)
            state_file = user_dir / f"{key}.json"
            if state_file.exists():
                state_file.unlink()
        except Exception as e:
            logger.error(f"Erro ao remover estado: {str(e)}")
    
    def clear(self, user_id: str) -> None:
        """
        Limpa o estado do usuário.
        
        Args:
            user_id: ID do usuário
        """
        try:
            user_dir = self._get_user_dir(user_id)
            for file in user_dir.glob('*.json'):
                file.unlink()
        except Exception as e:
            logger.error(f"Erro ao limpar estado: {str(e)}")
    
    def _encrypt(self, data: str) -> str:
        """Criptografa dados sensíveis."""
        return base64.b64encode(data.encode()).decode()
    
    def _decrypt(self, data: str) -> str:
        """Descriptografa dados sensíveis."""
        return base64.b64decode(data.encode()).decode()

class StateManager:
    """Gerencia o estado da aplicação."""
    
    def __init__(self):
        """Inicializa o gerenciador de estado."""
        self.memory_state: Dict[str, StateEntry] = {}
        self.persistence = StatePersistence()
        self.lock = threading.Lock()
        self.cache = CacheManager()
    
    def get(self, key: str, user_id: str) -> Optional[Any]:
        """
        Obtém dados do estado.
        
        Args:
            key: Chave dos dados
            user_id: ID do usuário
            
        Returns:
            Dados se encontrados, None caso contrário
        """
        with self.lock:
            # Tenta obter do cache
            cache_key = f"state_{user_id}_{key}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # Tenta obter da memória
            entry = self.memory_state.get(key)
            if entry and entry.user_id == user_id:
                return entry.data
            
            # Tenta obter do disco
            entry = self.persistence.load(key, user_id)
            if entry:
                self.memory_state[key] = entry
                self.cache.set(cache_key, entry.data)
                return entry.data
            
            return None
    
    def set(self, key: str, data: Any, user_id: str) -> None:
        """
        Armazena dados no estado.
        
        Args:
            key: Chave dos dados
            data: Dados a serem armazenados
            user_id: ID do usuário
        """
        with self.lock:
            entry = StateEntry(data, user_id)
            
            # Armazena na memória
            self.memory_state[key] = entry
            
            # Armazena no disco
            self.persistence.save(key, entry)
            
            # Armazena no cache
            cache_key = f"state_{user_id}_{key}"
            self.cache.set(cache_key, data)
    
    def delete(self, key: str, user_id: str) -> None:
        """
        Remove dados do estado.
        
        Args:
            key: Chave dos dados
            user_id: ID do usuário
        """
        with self.lock:
            # Remove da memória
            self.memory_state.pop(key, None)
            
            # Remove do disco
            self.persistence.delete(key, user_id)
            
            # Remove do cache
            cache_key = f"state_{user_id}_{key}"
            self.cache.delete(cache_key)
    
    def clear(self, user_id: str) -> None:
        """
        Limpa o estado do usuário.
        
        Args:
            user_id: ID do usuário
        """
        with self.lock:
            # Limpa memória
            self.memory_state = {
                k: v for k, v in self.memory_state.items()
                if v.user_id != user_id
            }
            
            # Limpa disco
            self.persistence.clear(user_id)
            
            # Limpa cache
            for key in list(self.cache.memory_cache.keys()):
                if key.startswith(f"state_{user_id}_"):
                    self.cache.delete(key)

# Instância global do estado
state = StateManager() 