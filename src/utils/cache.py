"""
Utilitário de cache para dados da API.

Este módulo implementa um sistema de cache para dados da API,
com suporte a expiração e persistência.

Estrutura:
1. CacheManager: Gerencia o cache em memória
2. CacheEntry: Representa uma entrada no cache
3. CachePersistence: Gerencia a persistência do cache

IMPORTANTE:
- Cache em memória para performance
- Persistência em disco para durabilidade
- Expiração automática de dados antigos
- Thread-safe para acesso concorrente
"""

import os
import json
import time
from typing import Any, Dict, Optional, TypeVar, Generic
from datetime import datetime, timedelta
import threading
from pathlib import Path

from src.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class CacheEntry(Generic[T]):
    """Representa uma entrada no cache."""
    
    def __init__(self, data: T, expiration: int):
        """
        Inicializa uma entrada no cache.
        
        Args:
            data: Dados a serem armazenados
            expiration: Tempo de expiração em segundos
        """
        self.data = data
        self.expiration = expiration
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou."""
        return time.time() - self.created_at > self.expiration
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a entrada para dicionário."""
        return {
            'data': self.data,
            'expiration': self.expiration,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry[T]':
        """Cria uma entrada a partir de um dicionário."""
        entry = cls(data['data'], data['expiration'])
        entry.created_at = data['created_at']
        return entry

class CachePersistence:
    """Gerencia a persistência do cache."""
    
    def __init__(self, cache_dir: str = '.cache'):
        """
        Inicializa o gerenciador de persistência.
        
        Args:
            cache_dir: Diretório para armazenar o cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, key: str, entry: CacheEntry) -> None:
        """
        Salva uma entrada no cache.
        
        Args:
            key: Chave da entrada
            entry: Entrada a ser salva
        """
        try:
            cache_file = self.cache_dir / f"{key}.json"
            with open(cache_file, 'w') as f:
                json.dump(entry.to_dict(), f)
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")
    
    def load(self, key: str) -> Optional[CacheEntry]:
        """
        Carrega uma entrada do cache.
        
        Args:
            key: Chave da entrada
            
        Returns:
            CacheEntry se encontrada, None caso contrário
        """
        try:
            cache_file = self.cache_dir / f"{key}.json"
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r') as f:
                data = json.load(f)
                entry = CacheEntry.from_dict(data)
                
                if entry.is_expired():
                    cache_file.unlink()
                    return None
                
                return entry
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {str(e)}")
            return None
    
    def clear(self) -> None:
        """Limpa o cache persistido."""
        try:
            for file in self.cache_dir.glob('*.json'):
                file.unlink()
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")

class CacheManager:
    """Gerencia o cache em memória e persistido."""
    
    def __init__(self, default_expiration: int = 3600):
        """
        Inicializa o gerenciador de cache.
        
        Args:
            default_expiration: Tempo padrão de expiração em segundos
        """
        self.default_expiration = default_expiration
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.persistence = CachePersistence()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtém dados do cache.
        
        Args:
            key: Chave dos dados
            
        Returns:
            Dados se encontrados, None caso contrário
        """
        with self.lock:
            # Tenta obter da memória
            entry = self.memory_cache.get(key)
            if entry and not entry.is_expired():
                return entry.data
            
            # Tenta obter do disco
            entry = self.persistence.load(key)
            if entry:
                self.memory_cache[key] = entry
                return entry.data
            
            return None
    
    def set(self, key: str, data: Any, expiration: Optional[int] = None) -> None:
        """
        Armazena dados no cache.
        
        Args:
            key: Chave dos dados
            data: Dados a serem armazenados
            expiration: Tempo de expiração em segundos
        """
        with self.lock:
            expiration = expiration or self.default_expiration
            entry = CacheEntry(data, expiration)
            
            # Armazena na memória
            self.memory_cache[key] = entry
            
            # Armazena no disco
            self.persistence.save(key, entry)
    
    def delete(self, key: str) -> None:
        """
        Remove dados do cache.
        
        Args:
            key: Chave dos dados
        """
        with self.lock:
            # Remove da memória
            self.memory_cache.pop(key, None)
            
            # Remove do disco
            cache_file = self.persistence.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
    
    def clear(self) -> None:
        """Limpa todo o cache."""
        with self.lock:
            self.memory_cache.clear()
            self.persistence.clear()
    
    def cleanup(self) -> None:
        """Remove entradas expiradas do cache."""
        with self.lock:
            # Limpa memória
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                self.memory_cache.pop(key)
            
            # Limpa disco
            for file in self.persistence.cache_dir.glob('*.json'):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        entry = CacheEntry.from_dict(data)
                        if entry.is_expired():
                            file.unlink()
                except:
                    file.unlink()

# Instância global do cache
cache = CacheManager() 