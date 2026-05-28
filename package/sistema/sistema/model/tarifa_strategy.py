from abc import ABC, abstractmethod
import math


class TarifaStrategy(ABC):
    @abstractmethod
    def calcular_tarifa(self, horas: float, tarifa_por_hora: float) -> float:
        pass


class TarifaPadrao(TarifaStrategy):
    def calcular_tarifa(self, horas: float, tarifa_por_hora: float) -> float:
        horas_cobradas = max(math.ceil(horas), 1)
        return horas_cobradas * tarifa_por_hora


class TarifaPernoite(TarifaStrategy):
    HORA_INICIO_PERNOITE = 22
    HORA_FIM_PERNOITE = 6
    TARIFA_PERNOITE_FIXA = 30.0

    def calcular_tarifa(self, horas: float, tarifa_por_hora: float) -> float:
        if horas >= 8:
            return self.TARIFA_PERNOITE_FIXA
        horas_cobradas = max(math.ceil(horas), 1)
        return horas_cobradas * tarifa_por_hora


class TarifaProgressiva(TarifaStrategy):
    def calcular_tarifa(self, horas: float, tarifa_por_hora: float) -> float:
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


TarifaProgessiva = TarifaProgressiva
