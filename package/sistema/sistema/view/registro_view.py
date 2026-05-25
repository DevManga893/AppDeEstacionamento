from typing import Any
from dataclasses import dataclass, field

from .view import View
from .placa_view import PlacaView


@dataclass
class RegistroView(View):
    placa_view: PlacaView
    descricao: Any
    placa_input: Any
    marca_selector: Any
    cor_selector: Any
    btn_registrar: Any
    feedback: Any
    placa: str = field(default="ABC1234")
    marca: str = field(default="Honda")
    cor: str = field(default="Azul")

    def atualizar_visual(self):
        self.placa_view.codigo_da_placa = self.placa
        self.descricao.textContent = f"{self.marca} - {self.cor} - {self.placa}"

    def mostrar_feedback(self, msg: str, cor_texto: str = "#80cbc4"):
        self.feedback.style.display = "block"
        self.feedback.style.color = cor_texto
        self.feedback.textContent = msg

    def ocultar_feedback(self):
        self.feedback.style.display = "none"
        self.feedback.textContent = ""
