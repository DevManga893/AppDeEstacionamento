from typing import Any
from dataclasses import dataclass

from .view import View


@dataclass
class PagamentoView(View):
    placa_input: Any
    btn_buscar: Any
    btn_pagar: Any
    btn_novo: Any
    resultado: Any
    erro: Any
    erro_texto: Any
    confirmacao: Any
    pag_placa: Any
    pag_marca: Any
    pag_cor: Any
    pag_entrada: Any
    pag_tempo: Any
    pag_total: Any
    pag_confirmacao_texto: Any

    def ocultar_tudo(self):
        self.erro.classList.remove("visivel")
        self.resultado.classList.remove("visivel")
        self.confirmacao.classList.remove("visivel")

    def mostrar_erro(self, msg: str):
        self.ocultar_tudo()
        self.erro_texto.textContent = msg
        self.erro.classList.add("visivel")

    def mostrar_resultado(self, dados: dict):
        self.ocultar_tudo()
        self.pag_placa.textContent = dados["placa"]
        self.pag_marca.textContent = dados["marca"]
        self.pag_cor.textContent = dados["cor"]
        self.pag_entrada.textContent = dados["entrada"]
        self.pag_tempo.textContent = dados["duracao_formatada"]
        total = dados["total"]
        self.pag_total.textContent = f"R$ {total:.2f}".replace(".", ",")
        self.resultado.classList.add("visivel")

    def mostrar_confirmacao(self, placa: str, total: float):
        total_fmt = f"R$ {total:.2f}".replace(".", ",")
        self.pag_confirmacao_texto.textContent = (
            f"Placa {placa} liberada. Total cobrado: {total_fmt}"
        )
        self.resultado.classList.remove("visivel")
        self.confirmacao.classList.add("visivel")

    def resetar(self):
        self.placa_input.value = ""
        self.ocultar_tudo()
