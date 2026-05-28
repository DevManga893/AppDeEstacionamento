"""
Módulo de gerenciamento de banco de dados com padrão Singleton.
Garante uma única instância do TinyDB para evitar problemas de concorrência.
"""
from typing import Optional
from tinydb import TinyDB
import threading


class DatabaseSingleton:
    """
    Implementa o padrão Singleton para gerenciar uma única instância do TinyDB.
    Thread-safe usando lock para evitar condições de corrida.
    """
    
    _instance: Optional['DatabaseSingleton'] = None
    _lock: threading.Lock = threading.Lock()
    _db: Optional[TinyDB] = None
    _caminho: str = "estacionamento.json"
    
    def __new__(cls, caminho: str = "estacionamento.json"):
        """
        Cria ou retorna a instância única do Singleton.
        
        Args:
            caminho: Caminho do arquivo JSON do TinyDB
            
        Returns:
            Instância única de DatabaseSingleton
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._caminho = caminho
                    cls._db = TinyDB(caminho)
        
        return cls._instance
    
    @classmethod
    def get_instance(cls, caminho: str = "estacionamento.json") -> 'DatabaseSingleton':
        """
        Obtém a instância única do Singleton.
        
        Args:
            caminho: Caminho do arquivo JSON do TinyDB
            
        Returns:
            Instância única de DatabaseSingleton
        """
        return cls(caminho)
    
    @classmethod
    def get_db(cls) -> TinyDB:
        """
        Obtém a instância do TinyDB.
        
        Returns:
            Instância do TinyDB
        """
        if cls._db is None:
            cls.get_instance()
        return cls._db
    
    def get_table(self, nome_tabela: str):
        """
        Obtém uma tabela do banco de dados.
        
        Args:
            nome_tabela: Nome da tabela
            
        Returns:
            Tabela do TinyDB
        """
        return self._db.table(nome_tabela)
    
    @classmethod
    def close(cls):
        """Fecha a conexão com o banco de dados."""
        if cls._db is not None:
            cls._db.close()
            cls._db = None
            cls._instance = None
    
    @classmethod
    def reset(cls):
        """Reseta a instância (útil para testes)."""
        cls.close()
