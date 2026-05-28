from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class EventoVeiculo:
    def __init__(self, tipo: str, placa: str, dados: Dict[str, Any]):
        self.tipo = tipo
        self.placa = placa
        self.dados = dados
        self.timestamp = datetime.now()

    def __repr__(self) -> str:
        return f"EventoVeiculo(tipo={self.tipo}, placa={self.placa}, timestamp={self.timestamp})"


class ObservadorVeiculo(ABC):
    @abstractmethod
    def atualizar(self, evento: EventoVeiculo) -> None:
        pass


class GerenciadorEventosVeiculo:
    instance = None
    lock = None

    def __new__(cls):
        if cls.instance is None:
            import threading
            if cls.lock is None:
                cls.lock = threading.Lock()
            with cls.lock:
                if cls.instance is None:
                    cls.instance = super().__new__(cls)
                    cls.instance.observadores: List[ObservadorVeiculo] = []
        return cls.instance

    @classmethod
    def get_instance(cls) -> 'GerenciadorEventosVeiculo':
        return cls()

    def registrar_observador(self, observador: ObservadorVeiculo) -> None:
        if observador not in self.observadores:
            self.observadores.append(observador)

    def remover_observador(self, observador: ObservadorVeiculo) -> None:
        if observador in self.observadores:
            self.observadores.remove(observador)

    def notificar_observadores(self, evento: EventoVeiculo) -> None:
        for observador in self.observadores:
            observador.atualizar(evento)

    def obter_observadores(self) -> List[ObservadorVeiculo]:
        return self.observadores.copy()

    def limpar_observadores(self) -> None:
        self.observadores.clear()


class AtualizadorPainelVagas(ObservadorVeiculo):
    def __init__(self, vagas_totais: int = 100):
        self.vagas_totais = vagas_totais
        self.vagas_ocupadas = 0

    def atualizar(self, evento: EventoVeiculo) -> None:
        if evento.tipo == "entrada":
            self.vagas_ocupadas += 1
            print(f"[PAINEL] Veículo {evento.placa} entrou. Vagas disponíveis: {self.vagas_totais - self.vagas_ocupadas}")
        elif evento.tipo == "saida":
            self.vagas_ocupadas = max(0, self.vagas_ocupadas - 1)
            print(f"[PAINEL] Veículo {evento.placa} saiu. Vagas disponíveis: {self.vagas_totais - self.vagas_ocupadas}")

    def obter_vagas_disponiveis(self) -> int:
        return self.vagas_totais - self.vagas_ocupadas


class AcionadorCancela(ObservadorVeiculo):
    def atualizar(self, evento: EventoVeiculo) -> None:
        if evento.tipo == "entrada":
            self.abrir_cancela_entrada(evento.placa)
        elif evento.tipo == "saida":
            self.abrir_cancela_saida(evento.placa)

    def abrir_cancela_entrada(self, placa: str) -> None:
        print(f"[CANCELA ENTRADA] Abrindo cancela para {placa}...")

    def abrir_cancela_saida(self, placa: str) -> None:
        print(f"[CANCELA SAÍDA] Abrindo cancela para {placa}...")


class RegistradorEventos(ObservadorVeiculo):
    def __init__(self):
        self.eventos_registrados: List[EventoVeiculo] = []

    def atualizar(self, evento: EventoVeiculo) -> None:
        self.eventos_registrados.append(evento)
        print(f"[LOG] {evento}")

    def obter_historico(self) -> List[EventoVeiculo]:
        return self.eventos_registrados.copy()
