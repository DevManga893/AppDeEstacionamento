# Documentação de Refatoração - Padrões GoF

## Visão Geral

Este documento descreve a refatoração do sistema de gerenciamento de estacionamento aplicando três padrões de projeto do Gang of Four (GoF):

1. **Strategy** - Para cálculo de tarifas intercambiáveis
2. **Singleton** - Para gerenciar instância única do banco de dados
3. **Observer** - Para notificação de eventos de entrada/saída

---

## 1. Padrão Strategy

### Objetivo
Isolar a lógica de cálculo de tarifa em estratégias intercambiáveis, permitindo diferentes formas de cobrança sem modificar o repositório.

### Implementação

#### Arquivo: `model/tarifa_strategy.py`

**Interface Abstrata:**
```python
class TarifaStrategy(ABC):
    @abstractmethod
    def calcular_tarifa(self, horas: float, tarifa_por_hora: float) -> float:
        pass
```

**Estratégias Concretas:**

1. **TarifaPadrao** - Estratégia padrão
   - Arredonda horas para cima (ceil)
   - Mínimo de 1 hora
   - Fórmula: `max(ceil(horas), 1) * tarifa_por_hora`

2. **TarifaPernoite** - Estratégia com tarifa fixa para pernoite
   - Permanência > 8 horas: tarifa fixa de R$ 30.00
   - Permanência ≤ 8 horas: tarifa padrão
   - Ideal para estacionamentos com promoção noturna

3. **TarifaProgessiva** - Estratégia com desconto progressivo
   - 1ª hora: tarifa normal
   - 2-5 horas: 80% da tarifa
   - Acima de 5 horas: 60% da tarifa
   - Incentiva permanência mais longa

### Uso

```python
from model.tarifa_strategy import TarifaPadrao, TarifaPernoite
from model.estacionamento_repository import EstacionamentoRepository

# Usar estratégia padrão
repo = EstacionamentoRepository()

# Usar estratégia pernoite
repo = EstacionamentoRepository(estrategia_tarifa=TarifaPernoite())

# Trocar estratégia dinamicamente
repo.definir_estrategia_tarifa(TarifaProgessiva())
```

### Benefícios
- ✅ Fácil adicionar novas estratégias sem modificar código existente
- ✅ Estratégias podem ser testadas isoladamente
- ✅ Permite trocar estratégia em tempo de execução
- ✅ Segue princípio Open/Closed (aberto para extensão, fechado para modificação)

---

## 2. Padrão Singleton

### Objetivo
Garantir que exista apenas uma instância do TinyDB ativa, evitando múltiplas conexões concorrentes ao arquivo JSON.

### Implementação

#### Arquivo: `model/database_singleton.py`

**Características:**
- Thread-safe usando `threading.Lock`
- Lazy initialization (cria instância apenas quando necessário)
- Método `get_instance()` para obter a instância única
- Método `close()` para fechar conexão
- Método `reset()` para testes

```python
class DatabaseSingleton:
    _instance = None
    _lock = threading.Lock()
    _db = None
    
    def __new__(cls, caminho: str = "estacionamento.json"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._db = TinyDB(caminho)
        return cls._instance
```

### Uso

```python
from model.database_singleton import DatabaseSingleton

# Primeira instância
db1 = DatabaseSingleton.get_instance()

# Segunda instância (retorna a mesma)
db2 = DatabaseSingleton.get_instance()

# Verificar que são a mesma instância
assert db1 is db2  # True

# Obter tabela
tabela = db1.get_table("veiculos")

# Fechar conexão
DatabaseSingleton.close()
```

### Benefícios
- ✅ Evita problemas de concorrência no arquivo JSON
- ✅ Reduz consumo de memória (uma única instância)
- ✅ Thread-safe para ambientes multi-thread
- ✅ Facilita testes com método `reset()`

### Integração no Repositório

O `EstacionamentoRepository` usa o Singleton internamente:

```python
class EstacionamentoRepository:
    def __init__(self, caminho: str = "estacionamento.json", ...):
        self.db_singleton = DatabaseSingleton.get_instance(caminho)
        self.tabela = self.db_singleton.get_table("veiculos")
```

---

## 3. Padrão Observer

### Objetivo
Implementar um mecanismo onde componentes secundários (painel de vagas, cancela, logs) possam se registrar para ouvir eventos de entrada e saída de veículos.

### Implementação

#### Arquivo: `model/evento_observer.py`

**Componentes Principais:**

1. **EventoVeiculo** - Representa um evento
   ```python
   class EventoVeiculo:
       tipo: str  # "entrada" ou "saida"
       placa: str
       dados: Dict[str, Any]
       timestamp: datetime
   ```

2. **ObservadorVeiculo** - Interface abstrata
   ```python
   class ObservadorVeiculo(ABC):
       @abstractmethod
       def atualizar(self, evento: EventoVeiculo) -> None:
           pass
   ```

3. **GerenciadorEventosVeiculo** - Gerenciador centralizado (Singleton)
   ```python
   class GerenciadorEventosVeiculo:
       def registrar_observador(self, observador: ObservadorVeiculo)
       def remover_observador(self, observador: ObservadorVeiculo)
       def notificar_observadores(self, evento: EventoVeiculo)
   ```

### Observadores Concretos Fornecidos

1. **AtualizadorPainelVagas**
   - Atualiza número de vagas disponíveis
   - Método: `obter_vagas_disponiveis()`

2. **AcionadorCancela**
   - Aciona cancela de entrada/saída
   - Métodos: `_abrir_cancela_entrada()`, `_abrir_cancela_saida()`

3. **RegistradorEventos**
   - Registra todos os eventos em log
   - Método: `obter_historico()`

### Uso

```python
from model.evento_observer import (
    GerenciadorEventosVeiculo,
    AtualizadorPainelVagas,
    AcionadorCancela,
    RegistradorEventos
)
from model.estacionamento_repository import EstacionamentoRepository

# Obter gerenciador (Singleton)
gerenciador = GerenciadorEventosVeiculo.get_instance()

# Criar observadores
painel = AtualizadorPainelVagas(vagas_totais=100)
cancela = AcionadorCancela()
registrador = RegistradorEventos()

# Registrar observadores
gerenciador.registrar_observador(painel)
gerenciador.registrar_observador(cancela)
gerenciador.registrar_observador(registrador)

# Criar repositório
repo = EstacionamentoRepository()

# Ao registrar entrada, todos os observadores são notificados
repo.registrar_entrada("ABC1234", "Honda", "Azul")
# Saída do console:
# [PAINEL] Veículo ABC1234 entrou. Vagas disponíveis: 99
# [CANCELA ENTRADA] Abrindo cancela para ABC1234...
# [LOG] EventoVeiculo(tipo=entrada, placa=ABC1234, ...)

# Ao registrar saída, novamente todos são notificados
repo.registrar_saida("ABC1234")
# Saída do console:
# [PAINEL] Veículo ABC1234 saiu. Vagas disponíveis: 100
# [CANCELA SAÍDA] Abrindo cancela para ABC1234...
# [LOG] EventoVeiculo(tipo=saida, placa=ABC1234, ...)
```

### Criar Observador Customizado

```python
from model.evento_observer import ObservadorVeiculo, EventoVeiculo

class MeuObservador(ObservadorVeiculo):
    def atualizar(self, evento: EventoVeiculo) -> None:
        if evento.tipo == "entrada":
            print(f"Veículo {evento.placa} entrou!")
        elif evento.tipo == "saida":
            print(f"Veículo {evento.placa} saiu!")

# Registrar
gerenciador = GerenciadorEventosVeiculo.get_instance()
meu_obs = MeuObservador()
gerenciador.registrar_observador(meu_obs)
```

### Benefícios
- ✅ Desacoplamento entre repositório e componentes secundários
- ✅ Fácil adicionar novos observadores sem modificar repositório
- ✅ Múltiplos observadores podem reagir ao mesmo evento
- ✅ Observadores podem ser adicionados/removidos em tempo de execução

---

## 4. Integração no EstacionamentoRepository

### Arquivo: `model/estacionamento_repository.py`

O repositório refatorado integra os três padrões:

```python
class EstacionamentoRepository:
    def __init__(
        self,
        caminho: str = "estacionamento.json",
        estrategia_tarifa: TarifaStrategy | None = None
    ):
        # Singleton: obtém instância única do banco
        self.db_singleton = DatabaseSingleton.get_instance(caminho)
        self.tabela = self.db_singleton.get_table("veiculos")
        
        # Strategy: define estratégia de tarifa
        self.estrategia_tarifa = estrategia_tarifa or TarifaPadrao()
        
        # Observer: obtém gerenciador de eventos
        self.gerenciador_eventos = GerenciadorEventosVeiculo.get_instance()
```

### Métodos Principais

#### `registrar_entrada(placa, marca, cor)`
- Registra entrada no banco
- **Dispara evento** de entrada para observadores
- Retorna mensagem de sucesso ou None

#### `buscar_veiculo(placa)`
- Busca veículo no banco
- **Usa Strategy** para calcular tarifa
- Retorna informações com tarifa calculada

#### `registrar_saida(placa)`
- Remove veículo do banco
- **Dispara evento** de saída para observadores
- Retorna placa e tarifa total

#### `definir_estrategia_tarifa(estrategia)`
- Permite trocar estratégia em tempo de execução

#### `listar_veiculos_estacionados()`
- Lista todos os veículos com tarifas calculadas

#### `obter_total_veiculos_estacionados()`
- Retorna número de veículos estacionados

---

## 5. Compatibilidade com Views e Controllers

### Assinaturas de Métodos Mantidas

As assinaturas dos métodos públicos foram mantidas para garantir compatibilidade:

```python
# Antes e Depois - Assinaturas Idênticas
def registrar_entrada(self, placa: str, marca: str | None, cor: str | None) -> dict | None
def buscar_veiculo(self, placa: str) -> dict | None
def registrar_saida(self, placa: str) -> dict | None
```

### Controllers Existentes

O `CancelaController` continua funcionando sem modificações:

```python
class CancelaController(Controller):
    def __init__(self):
        self.repositorio = EstacionamentoRepository()
    
    def entrada(self, veiculo: VeiculoModel) -> dict | None:
        return self.repositorio.registrar_entrada(
            veiculo.placa.upper(), veiculo.marca, veiculo.cor
        )
    
    def buscar(self, placa: str) -> dict | None:
        return self.repositorio.buscar_veiculo(placa)
    
    def saida(self, placa: str) -> dict | None:
        return self.repositorio.registrar_saida(placa)
```

### Views Existentes

As views (`PagamentoView`, `RegistroView`, `PlacaView`) continuam funcionando sem modificações, pois os dados retornados mantêm a mesma estrutura.

---

## 6. Exemplos de Uso

### Exemplo 1: Uso Básico
```python
repo = EstacionamentoRepository()
repo.registrar_entrada("ABC1234", "Honda", "Azul")
info = repo.buscar_veiculo("ABC1234")
repo.registrar_saida("ABC1234")
```

### Exemplo 2: Com Estratégia Customizada
```python
repo = EstacionamentoRepository(estrategia_tarifa=TarifaPernoite())
repo.registrar_entrada("ABC1234", "Honda", "Azul")
```

### Exemplo 3: Com Observadores
```python
gerenciador = GerenciadorEventosVeiculo.get_instance()
gerenciador.registrar_observador(AtualizadorPainelVagas(100))
gerenciador.registrar_observador(AcionadorCancela())

repo = EstacionamentoRepository()
repo.registrar_entrada("ABC1234", "Honda", "Azul")  # Notifica observadores
```

### Exemplo 4: Trocar Estratégia em Tempo de Execução
```python
repo = EstacionamentoRepository()
repo.registrar_entrada("ABC1234", "Honda", "Azul")

# Troca estratégia
repo.definir_estrategia_tarifa(TarifaProgessiva())
info = repo.buscar_veiculo("ABC1234")  # Usa nova estratégia
```

---

## 7. Testes

### Teste de Singleton
```python
repo1 = EstacionamentoRepository()
repo2 = EstacionamentoRepository()
assert repo1.db_singleton is repo2.db_singleton  # True
```

### Teste de Strategy
```python
repo1 = EstacionamentoRepository(estrategia_tarifa=TarifaPadrao())
repo2 = EstacionamentoRepository(estrategia_tarifa=TarifaPernoite())
# Mesmos dados, tarifas diferentes
```

### Teste de Observer
```python
gerenciador = GerenciadorEventosVeiculo.get_instance()
observador = RegistradorEventos()
gerenciador.registrar_observador(observador)

repo = EstacionamentoRepository()
repo.registrar_entrada("ABC1234", "Honda", "Azul")

assert len(observador.obter_historico()) == 1
```

---

## 8. Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    EstacionamentoRepository                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │  DatabaseSingleton│  │ TarifaStrategy   │  │  Gerenciador│ │
│  │   (Singleton)    │  │   (Strategy)     │  │  Eventos    │ │
│  │                  │  │                  │  │ (Observer)  │ │
│  │ - _instance      │  │ - calcular_tarifa│  │             │ │
│  │ - _db            │  │                  │  │ - registrar │ │
│  │ - get_instance() │  │ Implementações:  │  │ - remover   │ │
│  │ - get_table()    │  │ • TarifaPadrao   │  │ - notificar │ │
│  │ - close()        │  │ • TarifaPernoite │  │             │ │
│  │                  │  │ • TarifaProgessiva│ │ Observadores:│ │
│  └──────────────────┘  └──────────────────┘  │ • Painel    │ │
│                                               │ • Cancela   │ │
│                                               │ • Registrador│ │
│                                               └────────────┘ │
│                                                               │
│  Métodos Públicos:                                            │
│  - registrar_entrada()                                        │
│  - buscar_veiculo()                                           │
│  - registrar_saida()                                          │
│  - definir_estrategia_tarifa()                                │
│  - listar_veiculos_estacionados()                             │
│  - obter_total_veiculos_estacionados()                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Benefícios da Refatoração

### Antes
- ❌ Tarifa fixa no repositório
- ❌ Múltiplas instâncias de TinyDB possíveis
- ❌ Sem mecanismo para ações secundárias
- ❌ Difícil estender funcionalidades

### Depois
- ✅ Tarifas intercambiáveis via Strategy
- ✅ Instância única de banco de dados via Singleton
- ✅ Ações secundárias via Observer
- ✅ Fácil estender com novos padrões
- ✅ Código mais testável e manutenível
- ✅ Compatível com código existente

---

## 10. Próximos Passos

1. **Adicionar mais estratégias de tarifa** conforme necessário
2. **Criar observadores customizados** para integração com sistemas reais
3. **Implementar persistência de eventos** para auditoria
4. **Adicionar testes unitários** para cada padrão
5. **Documentar API** para consumidores do repositório

---

## Referências

- Gang of Four Design Patterns
- Strategy Pattern: https://refactoring.guru/design-patterns/strategy
- Singleton Pattern: https://refactoring.guru/design-patterns/singleton
- Observer Pattern: https://refactoring.guru/design-patterns/observer
