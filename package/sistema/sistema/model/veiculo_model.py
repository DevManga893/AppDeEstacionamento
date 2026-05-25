from .model import Model

class VeiculoModel(Model):
    placa: str
    marca: str | None=None
    cor: str | None=None