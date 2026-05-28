from datetime import datetime
from tinydb import Query

from .database_singleton import DatabaseSingleton
from .tarifa_strategy import TarifaStrategy, TarifaPadrao
from .evento_observer import GerenciadorEventosVeiculo, EventoVeiculo

TARIFA_POR_HORA = 5.0


class EstacionamentoRepository:
    def __init__(
        self,
        caminho: str = "estacionamento.json",
        estrategia_tarifa: TarifaStrategy | None = None
    ):
        self.db_singleton = DatabaseSingleton.get_instance(caminho)
        self.tabela = self.db_singleton.get_table("veiculos")
        self.estrategia_tarifa = estrategia_tarifa or TarifaPadrao()
        self.gerenciador_eventos = GerenciadorEventosVeiculo.get_instance()

    def definir_estrategia_tarifa(self, estrategia: TarifaStrategy) -> None:
        self.estrategia_tarifa = estrategia

    def registrar_entrada(self, placa: str, marca: str | None = None, cor: str | None = None) -> dict | None:
        V = Query()
        if self.tabela.search(V.placa == placa):
            return None
        self.tabela.insert({
            "placa": placa,
            "marca": marca or "Desconhecida",
            "cor": cor or "Desconhecida",
            "entrada": datetime.now().isoformat(),
        })
        evento = EventoVeiculo(
            tipo="entrada",
            placa=placa,
            dados={"marca": marca or "Desconhecida", "cor": cor or "Desconhecida"}
        )
        self.gerenciador_eventos.notificar_observadores(evento)
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
        total = self.estrategia_tarifa.calcular_tarifa(horas, TARIFA_POR_HORA)
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
        evento = EventoVeiculo(
            tipo="saida",
            placa=placa,
            dados={"total": info["total"], "duracao": info["duracao_formatada"]}
        )
        self.gerenciador_eventos.notificar_observadores(evento)
        return {"placa": placa, "total": info["total"]}

    def listar_veiculos_estacionados(self) -> list:
        veiculos = []
        for registro in self.tabela.all():
            entrada = datetime.fromisoformat(registro["entrada"])
            delta = datetime.now() - entrada
            horas = delta.total_seconds() / 3600
            total = self.estrategia_tarifa.calcular_tarifa(horas, TARIFA_POR_HORA)
            minutos_total = int(delta.total_seconds() // 60)
            duracao_fmt = f"{minutos_total // 60}h {minutos_total % 60:02d}min"
            veiculos.append({
                "placa": registro["placa"],
                "marca": registro["marca"],
                "cor": registro["cor"],
                "entrada": entrada.strftime("%d/%m/%Y %H:%M"),
                "duracao_formatada": duracao_fmt,
                "total": round(total, 2),
            })
        return veiculos

    def obter_total_veiculos_estacionados(self) -> int:
        return len(self.tabela.all())
