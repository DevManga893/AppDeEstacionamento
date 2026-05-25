import math
from datetime import datetime
from tinydb import TinyDB, Query

TARIFA_POR_HORA = 5.0


class EstacionamentoRepository:
    def __init__(self, caminho: str = "estacionamento.json"):
        self.db = TinyDB(caminho)
        self.tabela = self.db.table("veiculos")

    def registrar_entrada(self, placa: str, marca: str | None, cor: str | None) -> dict | None:
        V = Query()
        if self.tabela.search(V.placa == placa):
            return None
        self.tabela.insert({
            "placa": placa,
            "marca": marca or "Desconhecida",
            "cor": cor or "Desconhecida",
            "entrada": datetime.now().isoformat(),
        })
        return {"mensagem": f"Veículo {placa} registrado com sucesso."}

    def buscar_veiculo(self, placa: str) -> dict | None:
        V = Query()
        registros = self.tabela.search(V.placa == placa)
        if not registros:
            return None
        r = registros[0]
        entrada = datetime.fromisoformat(r["entrada"])
        delta = datetime.now() - entrada
        horas = delta.total_seconds() / 3600
        horas_cobradas = max(math.ceil(horas), 1)
        total = horas_cobradas * TARIFA_POR_HORA
        minutos_total = int(delta.total_seconds() // 60)
        duracao_fmt = f"{minutos_total // 60}h {minutos_total % 60:02d}min"
        return {
            "placa": r["placa"],
            "marca": r["marca"],
            "cor": r["cor"],
            "entrada": entrada.strftime("%d/%m/%Y %H:%M"),
            "duracao_formatada": duracao_fmt,
            "total": round(total, 2),
        }

    def registrar_saida(self, placa: str) -> dict | None:
        info = self.buscar_veiculo(placa)
        if info is None:
            return None
        V = Query()
        self.tabela.remove(V.placa == placa)
        return {"placa": placa, "total": info["total"]}
