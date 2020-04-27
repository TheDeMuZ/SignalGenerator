from copy import deepcopy

from numpy import arange

from .params import Params
import cps.signal.functions as func
from .functions import Function


class SignalOperationException(Exception):
    def __init__(self):
        super().__init__()


class Signal(Params):
    def __init__(self, signalType = None, A_re = None, A_im = None, t1 = 0.0, d = 0.0, T = None, kw = None, ts = None, p = None, f = 0.0, adc_f = None, adc_bits = None, dac_f = None):
        super().__init__(A_re, A_im, t1, d, T, kw, ts, p, f)
        
        self.adc_f = adc_f
        self.adc_bits = adc_bits
        self.dac_f = dac_f

        self.x_list = []
        self.y_list = []
        self.function = None

        if signalType == "Szum o rozkładzie jednostajnym":
            self.function = Function(func.uniformDistributionNoise, self)

        elif signalType == "Szum Gaussowski":
            self.function = Function(func.gaussianNoise, self)

        elif signalType == "Sygnał sinusoidalny":
            self.function = Function(func.sinusoidalSignal, self)

        elif signalType == "Sygnał sinusoidalny wyprostowany jednopołówkowo":
            self.function = Function(func.halfWaveRectified_sinusoidalSignal, self)

        elif signalType == "Sygnał sinusoidalny wyprostowany dwupołówkowo":
            self.function = Function(func.fullWaveRectified_sinusoidalSignal, self)

        elif signalType == "Sygnał prostokątny":
            self.function = Function(func.rectangularSignal, self)

        elif signalType == "Sygnał prostokątny symetryczny":
            self.function = Function(func.symmetrical_rectangularSignal, self)

        elif signalType == "Sygnał trójkątny":
            self.function = Function(func.triangularSignal, self)

        elif signalType == "Skok jednostkowy":
            self.function = Function(func.unitStepFunction, self)

        elif signalType == "Impuls jednostkowy":
            self.function = Function(func.unitImpulse, self)

        elif signalType == "Szum impulsowy":
            self.function = Function(func.unitNoise, self)

    def __check_compatibility(self, other):
        return (self.f == other.f) and (self.t1 == other.t1) and (self.d == other.d)

    def __check_signalTypes(self, other):
        return self.function and other.function and not (self.function.isRandom() or other.function.isRandom())

    def __add__(self, other):
        if not self.__check_compatibility(other):
            raise SignalOperationException()

        signal = deepcopy(self)
        signal.function = None

        for i in range(len(self.y_list)):
            signal.y_list[i] += other.y_list[i]

        if self.__check_signalTypes(other):
            signal.function = Function(self.function, self)
            signal.function.add(other.function, other)

        return signal

    def __sub__(self, other):
        if not self.__check_compatibility(other):
            raise SignalOperationException()

        signal = deepcopy(self)
        signal.function = None

        for i in range(len(self.y_list)):
            signal.y_list[i] -= other.y_list[i]

        if self.__check_signalTypes(other):
            signal.function = Function(self.function, self)
            signal.function.sub(other.function, other)

        return signal

    def __mul__(self, other):
        if not self.__check_compatibility(other):
            raise SignalOperationException()

        signal = deepcopy(self)
        signal.function = None

        for i in range(len(self.y_list)):
            signal.y_list[i] *= other.y_list[i]

        if self.__check_signalTypes(other):
            signal.function = Function(self.function, self)
            signal.function.mul(other.function, other)

        return signal

    def __truediv__(self, other):
        if not self.__check_compatibility(other):
            raise SignalOperationException()

        signal = deepcopy(self)
        signal.function = None

        for i in range(len(self.y_list)):
            signal.y_list[i] /= other.y_list[i]

        if self.__check_signalTypes(other):
            signal.function = Function(self.function, self)
            signal.function.div(other.function, other)

        return signal

    def __calculateParams(self):
        n1 = self.t1
        n2 = self.t1 + self.d
        factor = 1.0 / (n2 - n1 + 1)

        self.averageValue = factor * sum(self.y_list)

        self.absoluteAverageValue = factor * sum([abs(v) for v in self.y_list])

        self.averagePower = factor * sum([v * v for v in self.y_list])

        self.varianceAroundTheAverageValue = factor * sum([(v - self.averageValue) ** 2 for v in self.y_list])

        self.effectiveValue = self.averagePower ** 0.5

    def generate(self):
        if self.function:
            self.x_list.clear()
            self.y_list.clear()
            
            for time in arange(self.t1, self.t1 + self.d + 1.0 / self.f, 1.0 / self.f):
                self.x_list.append(time)
                self.y_list.append(self.function(None, time))

        self.__calculateParams()