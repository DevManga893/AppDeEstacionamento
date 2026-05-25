from typing import Any
from dataclasses import dataclass

from .view import View


@dataclass
class PlacaView(View):
    elemento_text: Any

    @property
    def codigo_da_placa(self) -> str:
        return self.elemento_text.textContent

    @codigo_da_placa.setter
    def codigo_da_placa(self, valor: str):
        self.elemento_text.textContent = valor
