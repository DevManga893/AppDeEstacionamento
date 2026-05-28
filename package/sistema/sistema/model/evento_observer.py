"""
Módulo de observadores de eventos.
Implementa o padrão Observer do GoF para disparar ações secundárias.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class EventoVeiculo:
    """Representa um evento de veículo (entrada ou saída)."""
    
    def __init__(self, tipo: str, placa: str, dados: Dict[str, Any]):
        """
        Inicializa um evento de veículo.
        
        Args:
            tipo: Tipo do evento ('entrada' ou 'saida')
            placa: Placa do veículo
            dados: Dados adicionais do evento
        """
        self.tipo = tipo
        self.placa = placa
        self.dados = dados
        self.timestamp = datetime.now()
    
    def __repr__(self) -> str:
        return f"EventoVeiculo(tipo={self.tipo}, placa={self.placa}, timestamp={self.timestamp})"


class ObservadorVeiculo(ABC):
    """Interface abstrata para observadores de eventos de veículos."""
    
    @abstractmethod
    def atualizar(self, evento: EventoVeiculo) -> None:
        """
        Chamado quando um evento de veículo ocorre.
        
        Args:
            evento: Evento de veículo que ocorreu
        """
        pass


class GerenciadorEventosVeiculo:
    """
    Gerenciador centralizado de eventos de veículos.
    Implementa o padrão Observer para notificar múltiplos observadores.
    """
    
    _instance = None
    _lock = None
    
    def __new__(cls):
        """Singleton para garantir um único gerenciador de eventos."""
        if cls._instance is None:
            import threading
            if cls._lock is None:
                cls._lock = threading.Lock()
            
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._observadores: List[ObservadorVeiculo] = []
        
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'GerenciadorEventosVeiculo':
        """
        Obtém a instância única do gerenciador.
        
        Returns:
            Instância única de GerenciadorEventosVeiculo
        """
        return cls()
    
    def registrar_observador(self, observador: ObservadorVeiculo) -> None:
        """
        Registra um observador para receber notificações de eventos.
        
        Args:
            observador: Observador a ser registrado
        """
        if observador not in self._observadores:
            self._observadores.append(observador)
    
    def remover_observador(self, observador: ObservadorVeiculo) -> None:
        """
        Remove um observador do registro.
        
        Args:
            observador: Observador a ser removido
        """
        if observador in self._observadores:
            self._observadores.remove(observador)
    
    def notificar_observadores(self, evento: EventoVeiculo) -> None:
        """
        Notifica todos os observadores registrados sobre um evento.
        
        Args:
            evento: Evento a ser notificado
        """
        for observador in self._observadores:
            observador.atualizar(evento)
    
    def obter_observadores(self) -> List[ObservadorVeiculo]:
        """
        Retorna lista de observadores registrados.
        
        Returns:
            Lista de observadores
        """
        return self._observadores.copy()
    
    def limpar_observadores(self) -> None:
        """Remove todos os observadores registrados."""
        self._observadores.clear()


# Exemplos de observadores concretos

class AtualizadorPainelVagas(ObservadorVeiculo):
    """Observador que atualiza o painel de vagas disponíveis."""
    
    def __init__(self, vagas_totais: int = 100):
        """
        Inicializa o atualizador de painel.
        
        Args:
            vagas_totais: Número total de vagas
        """
        self.vagas_totais = vagas_totais
        self.vagas_ocupadas = 0
    
    def atualizar(self, evento: EventoVeiculo) -> None:
        """
        Atualiza o painel quando um veículo entra ou sai.
        
        Args:
            evento: Evento de veículo
        """
        if evento.tipo == "entrada":
            self.vagas_ocupadas += 1
            print(f"[PAINEL] Veículo {evento.placa} entrou. "
                  f"Vagas disponíveis: {self.vagas_totais - self.vagas_ocupadas}")
        elif evento.tipo == "saida":
            self.vagas_ocupadas = max(0, self.vagas_ocupadas - 1)
            print(f"[PAINEL] Veículo {evento.placa} saiu. "
                  f"Vagas disponíveis: {self.vagas_totais - self.vagas_ocupadas}")
    
    def obter_vagas_disponiveis(self) -> int:
        """Retorna número de vagas disponíveis."""
        return self.vagas_totais - self.vagas_ocupadas


class AcionadorCancela(ObservadorVeiculo):
    """Observador que aciona a cancela de entrada/saída."""
    
    def atualizar(self, evento: EventoVeiculo) -> None:
        """
        Aciona a cancela quando um veículo entra ou sai.
        
        Args:
            evento: Evento de veículo
        """
        if evento.tipo == "entrada":
            self._abrir_cancela_entrada(evento.placa)
        elif evento.tipo == "saida":
            self._abrir_cancela_saida(evento.placa)
    
    def _abrir_cancela_entrada(self, placa: str) -> None:
        """Abre a cancela de entrada."""
        print(f"[CANCELA ENTRADA] Abrindo cancela para {placa}...")
        # Aqui iria a lógica real de acionamento da cancela
    
    def _abrir_cancela_saida(self, placa: str) -> None:
        """Abre a cancela de saída."""
        print(f"[CANCELA SAÍDA] Abrindo cancela para {placa}...")
        # Aqui iria a lógica real de acionamento da cancela


class RegistradorEventos(ObservadorVeiculo):
    """Observador que registra todos os eventos em log."""
    
    def __init__(self):
        """Inicializa o registrador de eventos."""
        self.eventos_registrados: List[EventoVeiculo] = []
    
    def atualizar(self, evento: EventoVeiculo) -> None:
        """
        Registra um evento em log.
        
        Args:
            evento: Evento de veículo
        """
        self.eventos_registrados.append(evento)
        print(f"[LOG] {evento}")
    
    def obter_historico(self) -> List[EventoVeiculo]:
        """Retorna histórico de eventos registrados."""
        return self.eventos_registrados.copy()
