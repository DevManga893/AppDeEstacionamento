from .controller import Controller
from ..model.veiculo_model import VeiculoModel
from ..model.estacionamento_repository import EstacionamentoRepository


class CancelaController(Controller):
    def __init__(self):
        self.repositorio = EstacionamentoRepository()

    def entrada(self, veiculo: VeiculoModel) -> dict | None:
        return self.repositorio.registrar_entrada(
            veiculo.placa.upper(), veiculo.marca, veiculo.cor
        )

    def buscar(self, placa: str) -> dict | None:
        return self.repositorio.buscar_veiculo(placa)

    def saida(self, placa: str) -> dict | None:
        return self.repositorio.registrar_saida(placa)
