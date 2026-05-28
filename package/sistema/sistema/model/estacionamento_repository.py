"""
Repositório de estacionamento refatorado com padrões GoF.
Utiliza Strategy para cálculo de tarifa, Singleton para banco de dados,
e Observer para notificação de eventos.
"""
from datetime import datetime
from tinydb import Query

from .database_singleton import DatabaseSingleton
from .tarifa_strategy import TarifaStrategy, TarifaPadrao
from .evento_observer import GerenciadorEventosVeiculo, EventoVeiculo

# Constante de tarifa padrão (pode ser alterada conforme necessário)
TARIFA_POR_HORA = 5.0


class EstacionamentoRepository:
    """
    Repositório de estacionamento com suporte a múltiplas estratégias de tarifa
    e notificação de eventos através do padrão Observer.
    """
    
    def __init__(
        self,
        caminho: str = "estacionamento.json",
        estrategia_tarifa: TarifaStrategy | None = None
    ):
        """
        Inicializa o repositório de estacionamento.
        
        Args:
            caminho: Caminho do arquivo JSON do TinyDB
            estrategia_tarifa: Estratégia de cálculo de tarifa (padrão: TarifaPadrao)
        """
        # Inicializa Singleton do banco de dados
        self.db_singleton = DatabaseSingleton.get_instance(caminho)
        self.tabela = self.db_singleton.get_table("veiculos")
        
        # Define estratégia de tarifa (padrão: TarifaPadrao)
        self.estrategia_tarifa = estrategia_tarifa or TarifaPadrao()
        
        # Obtém gerenciador de eventos (Singleton)
        self.gerenciador_eventos = GerenciadorEventosVeiculo.get_instance()
    
    def definir_estrategia_tarifa(self, estrategia: TarifaStrategy) -> None:
        """
        Define uma nova estratégia de cálculo de tarifa.
        
        Args:
            estrategia: Nova estratégia de tarifa
        """
        self.estrategia_tarifa = estrategia
    
    def registrar_entrada(self, placa: str, marca: str | None = None, cor: str | None = None) -> dict | None:
        """
        Registra a entrada de um veículo no estacionamento.
        Dispara evento de entrada para observadores.
        
        Args:
            placa: Placa do veículo
            marca: Marca do veículo (opcional)
            cor: Cor do veículo (opcional)
            
        Returns:
            Dicionário com mensagem de sucesso ou None se veículo já existe
        """
        V = Query()
        
        # Verifica se veículo já está estacionado
        if self.tabela.search(V.placa == placa):
            return None
        
        # Registra entrada no banco de dados
        self.tabela.insert({
            "placa": placa,
            "marca": marca or "Desconhecida",
            "cor": cor or "Desconhecida",
            "entrada": datetime.now().isoformat(),
        })
        
        # Dispara evento de entrada
        evento = EventoVeiculo(
            tipo="entrada",
            placa=placa,
            dados={
                "marca": marca or "Desconhecida",
                "cor": cor or "Desconhecida",
            }
        )
        self.gerenciador_eventos.notificar_observadores(evento)
        
        return {"mensagem": f"Veículo {placa} registrado com sucesso."}
    
    def buscar_veiculo(self, placa: str) -> dict | None:
        """
        Busca um veículo e calcula a tarifa usando a estratégia definida.
        
        Args:
            placa: Placa do veículo
            
        Returns:
            Dicionário com informações do veículo e tarifa, ou None se não encontrado
        """
        V = Query()
        registros = self.tabela.search(V.placa == placa)
        
        if not registros:
            return None
        
        r = registros[0]
        entrada = datetime.fromisoformat(r["entrada"])
        delta = datetime.now() - entrada
        horas = delta.total_seconds() / 3600
        
        # Usa estratégia de tarifa para calcular o valor
        total = self.estrategia_tarifa.calcular_tarifa(horas, TARIFA_POR_HORA)
        
        # Formata duração
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
        """
        Registra a saída de um veículo do estacionamento.
        Dispara evento de saída para observadores.
        
        Args:
            placa: Placa do veículo
            
        Returns:
            Dicionário com placa e tarifa total, ou None se veículo não encontrado
        """
        info = self.buscar_veiculo(placa)
        
        if info is None:
            return None
        
        # Remove veículo do banco de dados
        V = Query()
        self.tabela.remove(V.placa == placa)
        
        # Dispara evento de saída
        evento = EventoVeiculo(
            tipo="saida",
            placa=placa,
            dados={
                "total": info["total"],
                "duracao": info["duracao_formatada"],
            }
        )
        self.gerenciador_eventos.notificar_observadores(evento)
        
        return {"placa": placa, "total": info["total"]}
    
    def listar_veiculos_estacionados(self) -> list:
        """
        Lista todos os veículos atualmente estacionados.
        
        Returns:
            Lista de veículos com suas informações
        """
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
        """
        Retorna o número total de veículos estacionados.
        
        Returns:
            Número de veículos estacionados
        """
        return len(self.tabela.all())
