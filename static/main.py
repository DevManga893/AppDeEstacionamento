import json

from pyscript import fetch, window
from pyscript.ffi import create_proxy
from js import document

from sistema.view.placa_view import PlacaView
from sistema.view.registro_view import RegistroView
from sistema.view.pagamento_view import PagamentoView

M = window.M


def el(elem_id):
    return document.getElementById(elem_id)


class RegistroController:
    def __init__(self, view: RegistroView):
        self.view = view

    def on_placa_input(self, evt):
        self.view.placa = evt.target.value.upper()
        self.view.atualizar_visual()

    def on_marca_change(self, evt):
        self.view.marca = evt.target.value
        self.view.atualizar_visual()

    def on_cor_change(self, evt):
        self.view.cor = evt.target.value
        self.view.atualizar_visual()

    async def on_registrar(self, evt):
        evt.preventDefault()
        placa = self.view.placa.strip()
        if not placa:
            self.view.mostrar_feedback("⚠ Informe a placa antes de registrar.", "#ef9a9a")
            return
        corpo = json.dumps({
            "placa": placa,
            "marca": self.view.marca,
            "cor": self.view.cor,
        })
        resp = await fetch(
            "/api/veiculos",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=corpo,
        )
        data = json.loads(await resp.text())
        if resp.status == 201:
            self.view.mostrar_feedback(f"✔ {data['mensagem']}", "#80cbc4")
        elif resp.status == 409:
            self.view.mostrar_feedback(f"⚠ {data['detail']['erro']}", "#ef9a9a")
        else:
            erro = data.get("detail", {})
            msg = erro.get("erro", "Erro desconhecido.") if isinstance(erro, dict) else str(erro)
            self.view.mostrar_feedback(f"✘ {msg}", "#ef9a9a")

    def bind(self):
        self.view.placa_input.addEventListener("input", create_proxy(self.on_placa_input))
        self.view.marca_selector.addEventListener("change", create_proxy(self.on_marca_change))
        self.view.cor_selector.addEventListener("change", create_proxy(self.on_cor_change))
        self.view.btn_registrar.addEventListener("click", create_proxy(self.on_registrar))


class PagamentoController:
    def __init__(self, view: PagamentoView):
        self.view = view
        self.placa_em_pagamento = None

    async def on_buscar(self, evt):
        evt.preventDefault()
        placa = self.view.placa_input.value.strip().upper()
        if not placa:
            return
        resp = await fetch(f"/api/veiculos/{placa}", method="GET")
        self.view.ocultar_tudo()
        if resp.status == 404:
            self.view.mostrar_erro("Veículo não encontrado. Verifique a placa.")
            self.placa_em_pagamento = None
            return
        if resp.status != 200:
            self.view.mostrar_erro("Erro ao buscar veículo. Tente novamente.")
            self.placa_em_pagamento = None
            return
        data = json.loads(await resp.text())
        self.placa_em_pagamento = data["placa"]
        self.view.mostrar_resultado(data)

    async def on_pagar(self, evt):
        evt.preventDefault()
        if self.placa_em_pagamento is None:
            return
        resp = await fetch(f"/api/pagamento/{self.placa_em_pagamento}", method="POST")
        data = json.loads(await resp.text())
        if resp.status != 200:
            erro = data.get("detail", {})
            msg = erro.get("erro", "Erro ao processar pagamento.") if isinstance(erro, dict) else str(erro)
            self.view.mostrar_erro(msg)
            return
        self.view.mostrar_confirmacao(data["placa"], data["total"])
        self.placa_em_pagamento = None

    def on_novo_pagamento(self, evt):
        evt.preventDefault()
        self.view.resetar()
        self.placa_em_pagamento = None

    def bind(self):
        self.view.btn_buscar.addEventListener("click", create_proxy(self.on_buscar))
        self.view.btn_pagar.addEventListener("click", create_proxy(self.on_pagar))
        self.view.btn_novo.addEventListener("click", create_proxy(self.on_novo_pagamento))


registro_view = RegistroView(
    placa_view=PlacaView(el("placa:placa:texto")),
    descricao=el("descricao"),
    placa_input=el("placa-input"),
    marca_selector=el("marca-selector"),
    cor_selector=el("cor-selector"),
    btn_registrar=el("btn-registrar"),
    feedback=el("registro-feedback"),
)

pagamento_view = PagamentoView(
    placa_input=el("pagamento-placa-input"),
    btn_buscar=el("btn-buscar"),
    btn_pagar=el("btn-pagar"),
    btn_novo=el("btn-novo-pagamento"),
    resultado=el("pagamento-resultado"),
    erro=el("pagamento-erro"),
    erro_texto=el("pagamento-erro-texto"),
    confirmacao=el("pagamento-confirmacao"),
    pag_placa=el("pag-placa"),
    pag_marca=el("pag-marca"),
    pag_cor=el("pag-cor"),
    pag_entrada=el("pag-entrada"),
    pag_tempo=el("pag-tempo"),
    pag_total=el("pag-total"),
    pag_confirmacao_texto=el("pag-confirmacao-texto"),
)

registro_ctrl = RegistroController(registro_view)
pagamento_ctrl = PagamentoController(pagamento_view)

registro_view.atualizar_visual()
registro_ctrl.bind()
pagamento_ctrl.bind()
