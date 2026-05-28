import pytest
import os
import tempfile

from sistema.model.tarifa_strategy import TarifaPadrao, TarifaPernoite, TarifaProgressiva, TarifaProgessiva
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
from sistema.model.estacionamento_facade import EstacionamentoFacade


class TestTarifaStrategy:
    def test_tarifa_padrao_1_hora(self):
        estrategia = TarifaPadrao()
        assert estrategia.calcular_tarifa(1.0, 5.0) == 5.0

    def test_tarifa_padrao_minimo_1_hora(self):
        estrategia = TarifaPadrao()
        assert estrategia.calcular_tarifa(0.5, 5.0) == 5.0

    def test_tarifa_padrao_arredonda_para_cima(self):
        estrategia = TarifaPadrao()
        assert estrategia.calcular_tarifa(1.5, 5.0) == 10.0

    def test_tarifa_padrao_2_horas(self):
        estrategia = TarifaPadrao()
        assert estrategia.calcular_tarifa(2.0, 5.0) == 10.0

    def test_tarifa_padrao_zero_horas(self):
        estrategia = TarifaPadrao()
        assert estrategia.calcular_tarifa(0.0, 5.0) == 5.0

    def test_tarifa_padrao_exata_3_horas(self):
        estrategia = TarifaPadrao()
        assert estrategia.calcular_tarifa(3.0, 10.0) == 30.0

    def test_tarifa_pernoite_menos_8_horas(self):
        estrategia = TarifaPernoite()
        assert estrategia.calcular_tarifa(4.0, 5.0) == 20.0

    def test_tarifa_pernoite_mais_8_horas(self):
        estrategia = TarifaPernoite()
        assert estrategia.calcular_tarifa(10.0, 5.0) == 30.0

    def test_tarifa_pernoite_exatamente_8_horas(self):
        estrategia = TarifaPernoite()
        assert estrategia.calcular_tarifa(8.0, 5.0) == 30.0

    def test_tarifa_pernoite_minimo_1_hora(self):
        estrategia = TarifaPernoite()
        assert estrategia.calcular_tarifa(0.3, 5.0) == 5.0

    def test_tarifa_progressiva_1_hora(self):
        estrategia = TarifaProgressiva()
        assert estrategia.calcular_tarifa(1.0, 5.0) == 5.0

    def test_tarifa_progressiva_3_horas(self):
        estrategia = TarifaProgressiva()
        assert estrategia.calcular_tarifa(3.0, 5.0) == 13.0

    def test_tarifa_progressiva_6_horas(self):
        estrategia = TarifaProgressiva()
        assert estrategia.calcular_tarifa(6.0, 5.0) == 24.0

    def test_tarifa_progressiva_5_horas_fronteira(self):
        estrategia = TarifaProgressiva()
        tarifa = estrategia.calcular_tarifa(5.0, 5.0)
        assert tarifa == 5.0 + 4 * 4.0

    def test_tarifa_progressiva_0_horas_minimo(self):
        estrategia = TarifaProgressiva()
        assert estrategia.calcular_tarifa(0.0, 5.0) == 5.0

    def test_alias_tarifa_progessiva(self):
        assert TarifaProgessiva is TarifaProgressiva

    def test_tarifa_padrao_tarifa_diferente(self):
        estrategia = TarifaPadrao()
        assert estrategia.calcular_tarifa(2.0, 10.0) == 20.0


class TestDatabaseSingleton:
    def setup_method(self):
        DatabaseSingleton.reset()

    def teardown_method(self):
        DatabaseSingleton.reset()

    def test_singleton_mesma_instancia(self):
        db1 = DatabaseSingleton.get_instance()
        db2 = DatabaseSingleton.get_instance()
        assert db1 is db2

    def test_singleton_mesmo_banco_dados(self):
        db1 = DatabaseSingleton.get_instance()
        db2 = DatabaseSingleton.get_instance()
        assert db1.get_db() is db2.get_db()

    def test_singleton_mesma_tabela(self):
        db1 = DatabaseSingleton.get_instance()
        db2 = DatabaseSingleton.get_instance()
        tabela1 = db1.get_table("teste")
        tabela2 = db2.get_table("teste")
        assert tabela1 is tabela2

    def test_singleton_reset_cria_nova_instancia(self):
        db1 = DatabaseSingleton.get_instance()
        DatabaseSingleton.reset()
        db2 = DatabaseSingleton.get_instance()
        assert db1 is not db2

    def test_singleton_get_db_inicializa_se_necessario(self):
        db = DatabaseSingleton.get_db()
        assert db is not None


class TestObserver:
    def setup_method(self):
        GerenciadorEventosVeiculo.get_instance().limpar_observadores()

    def teardown_method(self):
        GerenciadorEventosVeiculo.get_instance().limpar_observadores()

    def test_registrar_observador(self):
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        observador = RegistradorEventos()
        gerenciador.registrar_observador(observador)
        assert observador in gerenciador.obter_observadores()

    def test_remover_observador(self):
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        observador = RegistradorEventos()
        gerenciador.registrar_observador(observador)
        gerenciador.remover_observador(observador)
        assert observador not in gerenciador.obter_observadores()

    def test_notificar_observadores(self):
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        observador = RegistradorEventos()
        gerenciador.registrar_observador(observador)
        evento = EventoVeiculo("entrada", "ABC1234", {"marca": "Honda"})
        gerenciador.notificar_observadores(evento)
        assert len(observador.obter_historico()) == 1
        assert observador.obter_historico()[0].placa == "ABC1234"

    def test_atualizador_painel_vagas_entrada(self):
        painel = AtualizadorPainelVagas(vagas_totais=100)
        painel.atualizar(EventoVeiculo("entrada", "ABC1234", {}))
        assert painel.obter_vagas_disponiveis() == 99

    def test_atualizador_painel_vagas_saida(self):
        painel = AtualizadorPainelVagas(vagas_totais=100)
        painel.atualizar(EventoVeiculo("entrada", "ABC1234", {}))
        painel.atualizar(EventoVeiculo("saida", "ABC1234", {}))
        assert painel.obter_vagas_disponiveis() == 100

    def test_painel_vagas_nao_negativo(self):
        painel = AtualizadorPainelVagas(vagas_totais=5)
        painel.atualizar(EventoVeiculo("saida", "ABC1234", {}))
        assert painel.obter_vagas_disponiveis() == 5

    def test_gerenciador_singleton(self):
        g1 = GerenciadorEventosVeiculo.get_instance()
        g2 = GerenciadorEventosVeiculo.get_instance()
        assert g1 is g2

    def test_nao_registra_observador_duplicado(self):
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        obs = RegistradorEventos()
        gerenciador.registrar_observador(obs)
        gerenciador.registrar_observador(obs)
        assert gerenciador.obter_observadores().count(obs) == 1

    def test_multiplos_observadores_notificados(self):
        gerenciador = GerenciadorEventosVeiculo.get_instance()
        obs1 = RegistradorEventos()
        obs2 = RegistradorEventos()
        gerenciador.registrar_observador(obs1)
        gerenciador.registrar_observador(obs2)
        gerenciador.notificar_observadores(EventoVeiculo("entrada", "XYZ", {}))
        assert len(obs1.obter_historico()) == 1
        assert len(obs2.obter_historico()) == 1

    def test_evento_veiculo_campos(self):
        evento = EventoVeiculo("saida", "PQR9876", {"total": 15.0})
        assert evento.tipo == "saida"
        assert evento.placa == "PQR9876"
        assert evento.dados["total"] == 15.0
        assert evento.timestamp is not None

    def test_registrador_historico(self):
        obs = RegistradorEventos()
        obs.atualizar(EventoVeiculo("entrada", "A", {}))
        obs.atualizar(EventoVeiculo("saida", "A", {}))
        historico = obs.obter_historico()
        assert len(historico) == 2
        assert historico[0].tipo == "entrada"
        assert historico[1].tipo == "saida"


class TestEstacionamentoRepository:
    def setup_method(self):
        DatabaseSingleton.reset()
        GerenciadorEventosVeiculo.get_instance().limpar_observadores()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def teardown_method(self):
        DatabaseSingleton.reset()
        GerenciadorEventosVeiculo.get_instance().limpar_observadores()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_registrar_entrada(self):
        repo = EstacionamentoRepository(self.db_path)
        resultado = repo.registrar_entrada("ABC1234", "Honda", "Azul")
        assert resultado is not None
        assert "mensagem" in resultado

    def test_registrar_entrada_duplicada(self):
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        assert repo.registrar_entrada("ABC1234", "Toyota", "Preto") is None

    def test_buscar_veiculo(self):
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        info = repo.buscar_veiculo("ABC1234")
        assert info is not None
        assert info["placa"] == "ABC1234"
        assert info["marca"] == "Honda"
        assert info["cor"] == "Azul"
        assert "total" in info

    def test_buscar_veiculo_inexistente(self):
        repo = EstacionamentoRepository(self.db_path)
        assert repo.buscar_veiculo("XYZ9999") is None

    def test_registrar_saida(self):
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        resultado = repo.registrar_saida("ABC1234")
        assert resultado is not None
        assert resultado["placa"] == "ABC1234"
        assert "total" in resultado

    def test_registrar_saida_inexistente(self):
        repo = EstacionamentoRepository(self.db_path)
        assert repo.registrar_saida("XYZ9999") is None

    def test_veiculo_removido_apos_saida(self):
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        repo.registrar_saida("ABC1234")
        assert repo.buscar_veiculo("ABC1234") is None

    def test_estrategia_padrao(self):
        repo = EstacionamentoRepository(self.db_path, estrategia_tarifa=TarifaPadrao())
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        assert repo.buscar_veiculo("ABC1234")["total"] >= 5.0

    def test_estrategia_pernoite(self):
        repo = EstacionamentoRepository(self.db_path, estrategia_tarifa=TarifaPernoite())
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        assert repo.buscar_veiculo("ABC1234")["total"] is not None

    def test_trocar_estrategia(self):
        repo = EstacionamentoRepository(self.db_path, estrategia_tarifa=TarifaPadrao())
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        tarifa1 = repo.buscar_veiculo("ABC1234")["total"]
        repo.definir_estrategia_tarifa(TarifaProgressiva())
        tarifa2 = repo.buscar_veiculo("ABC1234")["total"]
        assert tarifa1 is not None
        assert tarifa2 is not None

    def test_listar_veiculos_estacionados(self):
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        repo.registrar_entrada("XYZ5678", "Toyota", "Preto")
        veiculos = repo.listar_veiculos_estacionados()
        assert len(veiculos) == 2
        placas = [v["placa"] for v in veiculos]
        assert "ABC1234" in placas
        assert "XYZ5678" in placas

    def test_obter_total_veiculos_estacionados(self):
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        repo.registrar_entrada("XYZ5678", "Toyota", "Preto")
        assert repo.obter_total_veiculos_estacionados() == 2

    def test_total_veiculos_vazio(self):
        repo = EstacionamentoRepository(self.db_path)
        assert repo.obter_total_veiculos_estacionados() == 0

    def test_eventos_disparados(self):
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
        repo1 = EstacionamentoRepository(self.db_path)
        repo2 = EstacionamentoRepository(self.db_path)
        repo1.registrar_entrada("ABC1234", "Honda", "Azul")
        info = repo2.buscar_veiculo("ABC1234")
        assert info is not None

    def test_entrada_sem_marca_cor(self):
        repo = EstacionamentoRepository(self.db_path)
        resultado = repo.registrar_entrada("ABC1234")
        assert resultado is not None
        info = repo.buscar_veiculo("ABC1234")
        assert info["marca"] == "Desconhecida"
        assert info["cor"] == "Desconhecida"

    def test_buscar_retorna_campos_view(self):
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        info = repo.buscar_veiculo("ABC1234")
        for campo in ("placa", "marca", "cor", "entrada", "duracao_formatada", "total"):
            assert campo in info

    def test_saida_retorna_campos_controller(self):
        repo = EstacionamentoRepository(self.db_path)
        repo.registrar_entrada("ABC1234", "Honda", "Azul")
        resultado = repo.registrar_saida("ABC1234")
        assert "placa" in resultado
        assert "total" in resultado


class TestEstacionamentoFacade:
    def setup_method(self):
        DatabaseSingleton.reset()
        GerenciadorEventosVeiculo.get_instance().limpar_observadores()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def teardown_method(self):
        DatabaseSingleton.reset()
        GerenciadorEventosVeiculo.get_instance().limpar_observadores()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_facade_registrar_entrada(self):
        facade = EstacionamentoFacade(self.db_path)
        resultado = facade.registrar_entrada("abc1234", "Honda", "Azul")
        assert resultado is not None
        assert "mensagem" in resultado

    def test_facade_uppercase_placa(self):
        facade = EstacionamentoFacade(self.db_path)
        facade.registrar_entrada("abc1234", "Honda", "Azul")
        info = facade.buscar_veiculo("ABC1234")
        assert info is not None

    def test_facade_buscar_veiculo_inexistente(self):
        facade = EstacionamentoFacade(self.db_path)
        assert facade.buscar_veiculo("ZZZ9999") is None

    def test_facade_registrar_saida(self):
        facade = EstacionamentoFacade(self.db_path)
        facade.registrar_entrada("ABC1234", "Honda", "Azul")
        resultado = facade.registrar_saida("ABC1234")
        assert resultado is not None
        assert resultado["placa"] == "ABC1234"

    def test_facade_listar_veiculos(self):
        facade = EstacionamentoFacade(self.db_path)
        facade.registrar_entrada("AAA1111", "Honda", "Azul")
        facade.registrar_entrada("BBB2222", "Toyota", "Preto")
        veiculos = facade.listar_veiculos()
        assert len(veiculos) == 2

    def test_facade_total_veiculos(self):
        facade = EstacionamentoFacade(self.db_path)
        facade.registrar_entrada("AAA1111", "Honda", "Azul")
        assert facade.total_veiculos() == 1

    def test_facade_estrategia_padrao(self):
        facade = EstacionamentoFacade(self.db_path)
        facade.definir_estrategia_padrao()
        facade.registrar_entrada("ABC1234", "Honda", "Azul")
        assert facade.buscar_veiculo("ABC1234")["total"] >= 5.0

    def test_facade_estrategia_pernoite(self):
        facade = EstacionamentoFacade(self.db_path)
        facade.definir_estrategia_pernoite()
        facade.registrar_entrada("ABC1234", "Honda", "Azul")
        assert facade.buscar_veiculo("ABC1234")["total"] is not None

    def test_facade_estrategia_progressiva(self):
        facade = EstacionamentoFacade(self.db_path)
        facade.definir_estrategia_progressiva()
        facade.registrar_entrada("ABC1234", "Honda", "Azul")
        assert facade.buscar_veiculo("ABC1234")["total"] >= 5.0

    def test_facade_criar_observador_log(self):
        facade = EstacionamentoFacade(self.db_path)
        obs = facade.criar_observador_log()
        facade.registrar_entrada("ABC1234", "Honda", "Azul")
        assert len(obs.obter_historico()) == 1

    def test_facade_criar_observador_painel(self):
        facade = EstacionamentoFacade(self.db_path)
        painel = facade.criar_observador_painel(50)
        facade.registrar_entrada("ABC1234", "Honda", "Azul")
        assert painel.obter_vagas_disponiveis() == 49

    def test_facade_remover_observador(self):
        facade = EstacionamentoFacade(self.db_path)
        obs = facade.criar_observador_log()
        facade.remover_observador(obs)
        facade.registrar_entrada("ABC1234", "Honda", "Azul")
        assert len(obs.obter_historico()) == 0
