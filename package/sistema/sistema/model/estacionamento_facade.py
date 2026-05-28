from .estacionamento_repository import EstacionamentoRepository
from .tarifa_strategy import TarifaStrategy, TarifaPadrao, TarifaPernoite, TarifaProgressiva
from .evento_observer import (
    GerenciadorEventosVeiculo,
    ObservadorVeiculo,
    AtualizadorPainelVagas,
    AcionadorCancela,
    RegistradorEventos,
)


class EstacionamentoFacade:
    """
    Padrão Facade (GoF Estrutural): simplifica o acesso ao subsistema de
    estacionamento expondo uma interface única de alto nível.
    O cliente não precisa conhecer Repository, Strategy, Observer ou Singleton.
    """

    def __init__(self, caminho: str = "estacionamento.json"):
        self.repositorio = EstacionamentoRepository(caminho)
        self.gerenciador_eventos = GerenciadorEventosVeiculo.get_instance()

    def registrar_entrada(self, placa: str, marca: str | None = None, cor: str | None = None) -> dict | None:
        return self.repositorio.registrar_entrada(placa.upper(), marca, cor)

    def buscar_veiculo(self, placa: str) -> dict | None:
        return self.repositorio.buscar_veiculo(placa.upper())

    def registrar_saida(self, placa: str) -> dict | None:
        return self.repositorio.registrar_saida(placa.upper())

    def listar_veiculos(self) -> list:
        return self.repositorio.listar_veiculos_estacionados()

    def total_veiculos(self) -> int:
        return self.repositorio.obter_total_veiculos_estacionados()

    def definir_estrategia_padrao(self) -> None:
        self.repositorio.definir_estrategia_tarifa(TarifaPadrao())

    def definir_estrategia_pernoite(self) -> None:
        self.repositorio.definir_estrategia_tarifa(TarifaPernoite())

    def definir_estrategia_progressiva(self) -> None:
        self.repositorio.definir_estrategia_tarifa(TarifaProgressiva())

    def definir_estrategia(self, estrategia: TarifaStrategy) -> None:
        self.repositorio.definir_estrategia_tarifa(estrategia)

    def adicionar_observador(self, observador: ObservadorVeiculo) -> None:
        self.gerenciador_eventos.registrar_observador(observador)

    def remover_observador(self, observador: ObservadorVeiculo) -> None:
        self.gerenciador_eventos.remover_observador(observador)

    def criar_observador_log(self) -> RegistradorEventos:
        obs = RegistradorEventos()
        self.adicionar_observador(obs)
        return obs

    def criar_observador_painel(self, vagas_totais: int = 100) -> AtualizadorPainelVagas:
        obs = AtualizadorPainelVagas(vagas_totais)
        self.adicionar_observador(obs)
        return obs

    def criar_observador_cancela(self) -> AcionadorCancela:
        obs = AcionadorCancela()
        self.adicionar_observador(obs)
        return obs
