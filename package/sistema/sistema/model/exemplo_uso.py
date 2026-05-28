"""
Exemplo de uso do sistema de estacionamento refatorado com padrões GoF.
Demonstra como usar Strategy, Singleton e Observer.
"""

from .estacionamento_repository import EstacionamentoRepository
from .tarifa_strategy import TarifaPadrao, TarifaPernoite, TarifaProgessiva
from .evento_observer import (
    GerenciadorEventosVeiculo,
    AtualizadorPainelVagas,
    AcionadorCancela,
    RegistradorEventos,
)


def exemplo_basico():
    """Exemplo básico de uso do repositório com estratégia padrão."""
    print("=" * 60)
    print("EXEMPLO 1: Uso Básico com Estratégia Padrão")
    print("=" * 60)
    
    # Cria repositório com estratégia padrão
    repo = EstacionamentoRepository()
    
    # Registra entrada de veículos
    print("\n[ENTRADA] Registrando veículos...")
    repo.registrar_entrada("ABC1234", "Honda", "Azul")
    repo.registrar_entrada("XYZ5678", "Toyota", "Preto")
    
    # Busca informações de um veículo
    print("\n[BUSCA] Informações do veículo ABC1234:")
    info = repo.buscar_veiculo("ABC1234")
    if info:
        print(f"  Placa: {info['placa']}")
        print(f"  Marca: {info['marca']}")
        print(f"  Cor: {info['cor']}")
        print(f"  Entrada: {info['entrada']}")
        print(f"  Duração: {info['duracao_formatada']}")
        print(f"  Total: R$ {info['total']:.2f}")
    
    # Registra saída
    print("\n[SAÍDA] Registrando saída do veículo ABC1234...")
    saida = repo.registrar_saida("ABC1234")
    if saida:
        print(f"  Placa: {saida['placa']}")
        print(f"  Total a pagar: R$ {saida['total']:.2f}")


def exemplo_estrategia_pernoite():
    """Exemplo usando estratégia de tarifa pernoite."""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Estratégia de Tarifa Pernoite")
    print("=" * 60)
    
    # Cria repositório com estratégia pernoite
    repo = EstacionamentoRepository(estrategia_tarifa=TarifaPernoite())
    
    print("\n[ESTRATÉGIA] Usando TarifaPernoite (tarifa fixa para >8h)")
    repo.registrar_entrada("ABC1234", "Honda", "Azul")
    
    info = repo.buscar_veiculo("ABC1234")
    if info:
        print(f"  Placa: {info['placa']}")
        print(f"  Duração: {info['duracao_formatada']}")
        print(f"  Total: R$ {info['total']:.2f}")


def exemplo_estrategia_progressiva():
    """Exemplo usando estratégia de tarifa progressiva."""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Estratégia de Tarifa Progressiva")
    print("=" * 60)
    
    # Cria repositório com estratégia progressiva
    repo = EstacionamentoRepository(estrategia_tarifa=TarifaProgessiva())
    
    print("\n[ESTRATÉGIA] Usando TarifaProgessiva (desconto conforme tempo)")
    repo.registrar_entrada("ABC1234", "Honda", "Azul")
    
    info = repo.buscar_veiculo("ABC1234")
    if info:
        print(f"  Placa: {info['placa']}")
        print(f"  Duração: {info['duracao_formatada']}")
        print(f"  Total: R$ {info['total']:.2f}")


def exemplo_observer():
    """Exemplo usando padrão Observer com múltiplos observadores."""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Padrão Observer com Múltiplos Observadores")
    print("=" * 60)
    
    # Obtém gerenciador de eventos (Singleton)
    gerenciador = GerenciadorEventosVeiculo.get_instance()
    
    # Cria observadores
    painel = AtualizadorPainelVagas(vagas_totais=100)
    cancela = AcionadorCancela()
    registrador = RegistradorEventos()
    
    # Registra observadores
    print("\n[OBSERVADORES] Registrando observadores...")
    gerenciador.registrar_observador(painel)
    gerenciador.registrar_observador(cancela)
    gerenciador.registrar_observador(registrador)
    
    # Cria repositório
    repo = EstacionamentoRepository()
    
    # Registra entrada (dispara eventos)
    print("\n[ENTRADA] Registrando entrada de veículo...")
    repo.registrar_entrada("ABC1234", "Honda", "Azul")
    
    print(f"\nVagas disponíveis: {painel.obter_vagas_disponiveis()}")
    
    # Registra saída (dispara eventos)
    print("\n[SAÍDA] Registrando saída de veículo...")
    repo.registrar_saida("ABC1234")
    
    print(f"Vagas disponíveis: {painel.obter_vagas_disponiveis()}")
    
    # Mostra histórico de eventos
    print("\n[HISTÓRICO] Eventos registrados:")
    for evento in registrador.obter_historico():
        print(f"  - {evento}")


def exemplo_singleton():
    """Exemplo demonstrando o padrão Singleton."""
    print("\n" + "=" * 60)
    print("EXEMPLO 5: Padrão Singleton - Instância Única")
    print("=" * 60)
    
    # Cria dois repositórios
    repo1 = EstacionamentoRepository()
    repo2 = EstacionamentoRepository()
    
    # Verifica se usam a mesma instância de banco de dados
    print("\n[SINGLETON] Verificando instância única do banco de dados...")
    print(f"  repo1.db_singleton is repo2.db_singleton: {repo1.db_singleton is repo2.db_singleton}")
    print(f"  repo1.tabela is repo2.tabela: {repo1.tabela is repo2.tabela}")
    
    # Registra entrada em repo1
    print("\n[ENTRADA] Registrando entrada em repo1...")
    repo1.registrar_entrada("ABC1234", "Honda", "Azul")
    
    # Busca em repo2 (mesmo banco de dados)
    print("\n[BUSCA] Buscando em repo2 (mesmo banco de dados)...")
    info = repo2.buscar_veiculo("ABC1234")
    if info:
        print(f"  Veículo encontrado: {info['placa']}")
    
    # Limpa
    repo1.registrar_saida("ABC1234")


def exemplo_trocar_estrategia():
    """Exemplo de troca dinâmica de estratégia."""
    print("\n" + "=" * 60)
    print("EXEMPLO 6: Troca Dinâmica de Estratégia")
    print("=" * 60)
    
    # Cria repositório com estratégia padrão
    repo = EstacionamentoRepository(estrategia_tarifa=TarifaPadrao())
    
    print("\n[ESTRATÉGIA] Usando TarifaPadrao inicialmente...")
    repo.registrar_entrada("ABC1234", "Honda", "Azul")
    
    info = repo.buscar_veiculo("ABC1234")
    if info:
        print(f"  Total com TarifaPadrao: R$ {info['total']:.2f}")
    
    # Troca para estratégia progressiva
    print("\n[ESTRATÉGIA] Trocando para TarifaProgessiva...")
    repo.definir_estrategia_tarifa(TarifaProgessiva())
    
    info = repo.buscar_veiculo("ABC1234")
    if info:
        print(f"  Total com TarifaProgessiva: R$ {info['total']:.2f}")
    
    # Limpa
    repo.registrar_saida("ABC1234")


if __name__ == "__main__":
    # Executa exemplos
    exemplo_basico()
    exemplo_estrategia_pernoite()
    exemplo_estrategia_progressiva()
    exemplo_observer()
    exemplo_singleton()
    exemplo_trocar_estrategia()
    
    print("\n" + "=" * 60)
    print("Exemplos concluídos!")
    print("=" * 60)
