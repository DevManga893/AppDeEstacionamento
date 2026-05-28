"""
Módulo de estratégias de cálculo de tarifa.
Implementa o padrão Strategy do GoF para permitir diferentes formas de cálculo.
"""
from abc import ABC, abstractmethod
import math
from datetime import datetime


class TarifaStrategy(ABC):
    """Interface abstrata para estratégias de cálculo de tarifa."""
    
    @abstractmethod
    def calcular_tarifa(self, horas: float, tarifa_por_hora: float) -> float:
        """
        Calcula a tarifa baseada nas horas de permanência.
        
        Args:
            horas: Número de horas de permanência
            tarifa_por_hora: Valor da tarifa por hora
            
        Returns:
            Valor total da tarifa
        """
        pass


class TarifaPadrao(TarifaStrategy):
    """
    Estratégia padrão: cobra pelo tempo arredondado para cima (ceil).
    Mínimo de 1 hora.
    """
    
    def calcular_tarifa(self, horas: float, tarifa_por_hora: float) -> float:
        """
        Calcula tarifa padrão com arredondamento para cima.
        
        Args:
            horas: Número de horas de permanência
            tarifa_por_hora: Valor da tarifa por hora
            
        Returns:
            Valor total da tarifa (mínimo 1 hora)
        """
        horas_cobradas = max(math.ceil(horas), 1)
        return horas_cobradas * tarifa_por_hora


class TarifaPernoite(TarifaStrategy):
    """
    Estratégia pernoite: tarifa fixa para permanência noturna (22h às 6h).
    Fora desse horário, usa tarifa padrão.
    """
    
    HORA_INICIO_PERNOITE = 22
    HORA_FIM_PERNOITE = 6
    TARIFA_PERNOITE_FIXA = 30.0
    
    def calcular_tarifa(self, horas: float, tarifa_por_hora: float) -> float:
        """
        Calcula tarifa com desconto para pernoite.
        
        Args:
            horas: Número de horas de permanência
            tarifa_por_hora: Valor da tarifa por hora
            
        Returns:
            Valor total da tarifa (com desconto se pernoite)
        """
        # Se permanência é maior que 8 horas, aplica tarifa pernoite
        if horas >= 8:
            return self.TARIFA_PERNOITE_FIXA
        
        # Caso contrário, usa tarifa padrão
        horas_cobradas = max(math.ceil(horas), 1)
        return horas_cobradas * tarifa_por_hora


class TarifaProgessiva(TarifaStrategy):
    """
    Estratégia progressiva: quanto mais tempo, menor o valor por hora.
    Primeira hora: tarifa normal
    Próximas 4 horas: 80% da tarifa
    Acima de 5 horas: 60% da tarifa
    """
    
    def calcular_tarifa(self, horas: float, tarifa_por_hora: float) -> float:
        """
        Calcula tarifa com desconto progressivo.
        
        Args:
            horas: Número de horas de permanência
            tarifa_por_hora: Valor da tarifa por hora
            
        Returns:
            Valor total da tarifa com desconto progressivo
        """
        horas_cobradas = max(math.ceil(horas), 1)
        
        if horas_cobradas <= 1:
            return tarifa_por_hora
        elif horas_cobradas <= 5:
            primeira_hora = tarifa_por_hora
            horas_restantes = (horas_cobradas - 1) * (tarifa_por_hora * 0.8)
            return primeira_hora + horas_restantes
        else:
            primeira_hora = tarifa_por_hora
            proximas_4 = 4 * (tarifa_por_hora * 0.8)
            restante = (horas_cobradas - 5) * (tarifa_por_hora * 0.6)
            return primeira_hora + proximas_4 + restante
