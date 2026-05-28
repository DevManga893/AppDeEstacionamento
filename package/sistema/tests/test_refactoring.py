"""
Testes para validar a refatoração com padrões GoF.
Testa Strategy, Singleton e Observer.
"""
import pytest
import os
import tempfile
from datetime import datetime, timedelta

from sistema.model.tarifa_strategy import TarifaPadrao, TarifaPernoite, TarifaProgessiva
from sistema.model.database_singleton import DatabaseSingleton
from sistema.model.evento_observer import (
    GerenciadorEventosVeiculo,
    EventoVeiculo,
    ObservadorVeiculo,
    AtualizadorPainelVagas,
    AcionadorCancela,
    RegistradorEventos,
)
from sistema.model.estacionamento_repository import EstacionamentoRepository


class TestTarifaStrategy:
    """Testes para o padrão Strategy de cálculo de tarifa."""
    
    def test_tarifa_padrao_1_hora(self):
        """Testa tarifa padrão para 1 hora."""
        estrategia = TarifaPadrao()
        tarifa = estrategia.calcular_tarifa(1.0, 5.0)
        assert tarifa == 5.0
    
    def test_tarifa_padrao_minimo_1_hora(self):
        """Testa tarifa padrão com mínimo de 1 hora."""
        estrategia = TarifaPadrao()
        tarifa = estrategia.calcular_tarifa(0.5, 5.0)
        assert tarifa == 5.0
    
    def test_tarifa_padrao_arredonda_para_cima(self):
        """Testa arredondamento para cima."""
        estrategia = TarifaPadrao()
        tarifa = estrategia.calcular_tarifa(1.5, 5.0)
        assert tarifa == 10.0  # ceil(1.5) = 2 horas
    
    def test_tarifa_pernoite_menos_8_horas(self):
        """Testa tarifa pernoite com menos de 8 horas."""
        estrategia = TarifaPernoite()
        tarifa = estrategia.calcular_tarifa(4.0, 5.0)
        assert tarifa == 20.0  # 4 horas * 5.0
    
    def test_tarifa_pernoite_mais_8_horas(self):
        """Testa tarifa pernoite com mais de 8 horas."""
        estrategia = TarifaPernoite()
        tarifa = estrategia.calcular_tarifa(10.0, 5.0)
        assert tarifa == 30.0  # Tarifa fixa
    
    def test_tarifa_progressiva_1_hora(self):
        """Testa tarifa progressiva para 1 hora."""
        estrategia = TarifaProgessiva()
        tarifa = estrategia.calcular_tarifa(1.0, 5.0)
        assert tarifa == 5.0
    
    def test_tarifa_progressiva_3_horas(self):
        """Testa tarifa progressiva para 3 horas."""
        estrategia = TarifaProgessiva()
        tarifa = estrategia.calcular_tarifa(3.0, 5.0)
        # 1ª hora: 5.0, 2-3 horas: 2 * (5.0 * 0.8) = 8.0
        # Total: 5.0 + 8.0 = 13.0
        assert tarifa == 13.0
    
    def test_tarifa_progressiva_6_horas(self):
        """Testa tarifa progressiva para 6 horas."""
        estrategia = TarifaProgessiva()
        tarifa = estrategia.calcular_tarifa(6.0, 5.0)
        # 1ª hora: 5.0
        # 2-5 horas: 4 * (5.0 * 0.8) = 16.0
        # 6ª hora: 1 * (5.0 * 0.6) = 3.0
        # Total: 5.0 + 16.0 + 3.0 = 24.0
        assert tarifa == 24.0


class TestDatabaseSingleton:
    """Testes para o padrão Singleton do banco de dados."""
    
    def setup_method(self):
        """Limpa Singleton antes de cada teste."""
        DatabaseSingleton.reset()
    
    def teardown_method(self):
        """Limpa Singleton após cada teste."""
        DatabaseSingleton.reset()
    
    def test_singleton_mesma_instancia(self):
        """Testa se Singleton retorna a mesma instância."""
        db1 = DatabaseSingleton.get_instance()
        db2 = DatabaseSingleton.get_instance()
        assert db1 is db2
    
    def test_singleton_mesmo_banco_dados(self):
        """Testa se Singleton usa o mesmo banco de dados."""
        db1 = DatabaseSingleton.get_instance()
        db2 = DatabaseSingleton.get_instance()
        assert db1.get_db() is db2.get_db()
    
    def test_singleton_mesma_tabela(self):
        """Testa se Singleton retorna a mesma tabela."""
        db1 = DatabaseSingleton.get_instance()
        db2 = DatabaseSingleton.get_instance()
        tabela1 = db1.get_table("teste")
        tabela2 = db2.get_table("teste")
        assert tabela1 is tabela2


class TestObserver:
    """Testes para o padrão Observer."""
    
    def setup_method(self):
        """Limpa gerenciador de eventos antes de cada teste."""
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        gerenciador.limpar_observadores()
    
    def teardown_method(self):
        """Limpa gerenciador de eventos após cada teste."""
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        gerenciador.limpar_observadores()
    
    def test_registrar_observador(self):
        """Testa registro de observador."""
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        observador = RegistradorEventos()
        gerenciador.registrar_observador(observador)
        
        assert observador in gerenciador.obter_observadores()
    
    def test_remover_observador(self):
        """Testa remoção de observador."""
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        observador = RegistradorEventos()
        gerenciador.registrar_observador(observador)
        gerenciador.remover_observador(observador)
        
        assert observador not in gerenciador.obter_observadores()
    
    def test_notificar_observadores(self):
        """Testa notificação de observadores."""
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        observador = RegistradorEventos()
        gerenciador.registrar_observador(observador)
        
        evento = EventoVeiculo("entrada", "ABC1234", {"marca": "Honda"})
        gerenciador.notificar_observadores(evento)
        
        assert len(observador.obter_historico()) == 1
        assert observador.obter_historico()[0].placa == "ABC1234"
    
    def test_atualizador_painel_vagas(self):
        """Testa atualizador de painel de vagas."""
        painel = AtualizadorPainelVagas(vagas_totais=100)
        
        evento_entrada = EventoVeiculo("entrada", "ABC1234", {})
        painel.atualizar(evento_entrada)
        assert painel.obter_vagas_disponiveis() == 99
        
        evento_saida = EventoVeiculo("saida", "ABC1234", {})
        painel.atualizar(evento_saida)
        assert painel.obter_vagas_disponiveis() == 100


class TestEstacionamentoRepository:
    """Testes para o repositório refatorado."""
    
    def setup_method(self):
        """Configura ambiente de teste."""
        DatabaseSingleton.reset()
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        gerenciador.limpar_observadores()
        
        # Cria arquivo temporário para testes
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_db.close()
        self.db_path = self.temp_db.name
    
    def teardown_method(self):
        """Limpa ambiente de teste."""
        DatabaseSingleton.reset()
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        gerenciador.limpar_observadores()
        
        # Remove arquivo temporário
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_registrar_entrada(self):
        """Testa registro de entrada."""
        repo = EstacionamentoRepository(self.db_path)
        resultado = repo.registrar_entrada("ABC1234", "Honda", "Azul")
        
        assert resultado is not None
        assert "mensagem" in resultado
    
    def test_registrar_entrada_duplicada(self):
        """Testa que não permite entrada duplicada."""
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        resultado = repo.registrar_entrada("ABC1234", "Toyota", "Preto")
        
        assert resultado is None
    
    def test_buscar_veiculo(self):
        """Testa busca de veículo."""
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        info = repo.buscar_veiculo("ABC1234")
        
        assert info is not None
        assert info["placa"] == "ABC1234"
        assert info["marca"] == "Honda"
        assert info["cor"] == "Azul"
        assert "total" in info
    
    def test_buscar_veiculo_inexistente(self):
        """Testa busca de veículo inexistente."""
        repo = EstacionamentoRepository(self.db_path)
        info = repo.buscar_veiculo("XYZ9999")
        
        assert info is None
    
    def test_registrar_saida(self):
        """Testa registro de saída."""
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        resultado = repo.registrar_saida("ABC1234")
        
        assert resultado is not None
        assert resultado["placa"] == "ABC1234"
        assert "total" in resultado
    
    def test_registrar_saida_inexistente(self):
        """Testa saída de veículo inexistente."""
        repo = EstacionamentoRepository(self.db_path)
        resultado = repo.registrar_saida("XYZ9999")
        
        assert resultado is None
    
    def test_estrategia_padrao(self):
        """Testa repositório com estratégia padrão."""
        repo = EstacionamentoRepository(self.db_path, estrategia_tarifa=TarifaPadrao())
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        info = repo.buscar_veiculo("ABC1234")
        
        # Mínimo 1 hora = 5.0
        assert info["total"] >= 5.0
    
    def test_estrategia_pernoite(self):
        """Testa repositório com estratégia pernoite."""
        repo = EstacionamentoRepository(self.db_path, estrategia_tarifa=TarifaPernoite())
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        info = repo.buscar_veiculo("ABC1234")
        
        # Deve ter tarifa calculada
        assert info["total"] is not None
    
    def test_trocar_estrategia(self):
        """Testa troca dinâmica de estratégia."""
        repo = EstacionamentoRepository(self.db_path, estrategia_tarifa=TarifaPadrao())
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        
        info1 = repo.buscar_veiculo("ABC1234")
        tarifa1 = info1["total"]
        
        # Troca estratégia
        repo.definir_estrategia_tarifa(TarifaProgessiva())
        info2 = repo.buscar_veiculo("ABC1234")
        tarifa2 = info2["total"]
        
        # Tarifas podem ser diferentes
        assert tarifa1 is not None
        assert tarifa2 is not None
    
    def test_listar_veiculos_estacionados(self):
        """Testa listagem de veículos estacionados."""
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        repo.registrar_entrada("XYZ5678", "Toyota", "Preto")
        
        veiculos = repo.listar_veiculos_estacionados()
        
        assert len(veiculos) == 2
        placas = [v["placa"] for v in veiculos]
        assert "ABC1234" in placas
        assert "XYZ5678" in placas
    
    def test_obter_total_veiculos_estacionados(self):
        """Testa contagem de veículos estacionados."""
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        repo.registrar_entrada("XYZ5678", "Toyota", "Preto")
        
        total = repo.obter_total_veiculos_estacionados()
        
        assert total == 2
    
    def test_eventos_disparados(self):
        """Testa se eventos são disparados corretamente."""
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        registrador = RegistradorEventos()
        gerenciador.registrar_observador(registrador)
        
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        repo.registrar_saida("ABC1234")
        
        historico = registrador.obter_historico()
        assert len(historico) == 2
        assert historico[0].tipo == "entrada"
        assert historico[1].tipo == "saida"
    
    def test_singleton_compartilhado(self):
        """Testa se dois repositórios compartilham o mesmo banco."""
        repo1 = EstacionamentoRepository(self.db_path)
        repo2 = EstacionamentoRepository(self.db_path)
        
        repo1.registrar_entrada("ABC1234", "Honda", "Azul")
        info = repo2.buscar_veiculo("ABC1234")
        
        assert info is not None
        assert info["placa"] == "ABC1234"


class TestCompatibilidadeComViews:
    """Testes para garantir compatibilidade com Views existentes."""
    
    def setup_method(self):
        """Configura ambiente de teste."""
        DatabaseSingleton.reset()
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        gerenciador.limpar_observadores()
        
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_db.close()
        self.db_path = self.temp_db.name
    
    def teardown_method(self):
        """Limpa ambiente de teste."""
        DatabaseSingleton.reset()
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        gerenciador.limpar_observadores()
        
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_retorno_buscar_veiculo_compativel(self):
        """Testa se retorno de buscar_veiculo é compatível com PagamentoView."""
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        info = repo.buscar_veiculo("ABC1234")
        
        # Verifica campos esperados pela PagamentoView
        assert "placa" in info
        assert "marca" in info
        assert "cor" in info
        assert "entrada" in info
        assert "duracao_formatada" in info
        assert "total" in info
    
    def test_retorno_registrar_entrada_compativel(self):
        """Testa se retorno de registrar_entrada é compatível com RegistroView."""
        repo = EstacionamentoRepository(self.db_path)
        resultado = repo.registrar_entrada("ABC1234", "Honda", "Azul")
        
        # Verifica que retorna dicionário com mensagem
        assert resultado is not None
        assert "mensagem" in resultado
    
    def test_retorno_registrar_saida_compativel(self):
        """Testa se retorno de registrar_saida é compatível com CancelaController."""
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        resultado = repo.registrar_saida("ABC1234")
        
        # Verifica que retorna dicionário com placa e total
        assert resultado is not None
        assert "placa" in resultado
        assert "total" in resultado
