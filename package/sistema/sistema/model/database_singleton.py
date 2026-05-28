from typing import Optional
from tinydb import TinyDB
import threading


class DatabaseSingleton:
    instance: Optional['DatabaseSingleton'] = None
    lock: threading.Lock = threading.Lock()
    db: Optional[TinyDB] = None
    caminho: str = "estacionamento.json"

    def __new__(cls, caminho: str = "estacionamento.json"):
        if cls.instance is None:
            with cls.lock:
                if cls.instance is None:
                    cls.instance = super().__new__(cls)
                    cls.caminho = caminho
                    cls.db = TinyDB(caminho)
        return cls.instance

    @classmethod
    def get_instance(cls, caminho: str = "estacionamento.json") -> 'DatabaseSingleton':
        return cls(caminho)

    @classmethod
    def get_db(cls) -> TinyDB:
        if cls.db is None:
            cls.get_instance()
        return cls.db

    def get_table(self, nome_tabela: str):
        return self.db.table(nome_tabela)

    @classmethod
    def close(cls):
        if cls.db is not None:
            cls.db.close()
            cls.db = None
            cls.instance = None

    @classmethod
    def reset(cls):
        cls.close()
