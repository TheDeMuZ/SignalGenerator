import math
import random as rng


from .params import Params


def __sin(signal, time):
    return math.sin(2 * math.pi / signal.T * (time - signal.t1))


def uniformDistributionNoise(signal, time):
    value_re = rng.uniform(-signal.A.real, signal.A.real)
    value_im = rng.uniform(-signal.A.imag, signal.A.imag)
    return complex(value_re, value_im)


def gaussianNoise(signal, time):
    return complex(rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0))


def sinusoidalSignal(signal, time):
    return signal.A * __sin(signal, time)


def halfWaveRectified_sinusoidalSignal(signal, time):
    return 0.5 * signal.A * __sin(signal, time) + abs(__sin(signal, time))


def fullWaveRectified_sinusoidalSignal(signal, time):
    return signal.A * abs(__sin(signal, time))


def rectangularSignal(signal, time):
    k = math.floor(time / signal.T)

    if (time >= k * signal.T + signal.t1) and (time < signal.kw * signal.T + k * signal.T + signal.t1):
        return signal.A

    return complex(0.0, 0.0)


def symmetrical_rectangularSignal(signal, time):
    k = math.floor(time / signal.T)

    if (time >= k * signal.T + signal.t1) and (time < signal.kw * signal.T + k * signal.T + signal.t1):
        return signal.A

    return -signal.A


def triangularSignal(signal, time):
    k = math.floor(time / signal.T)

    if (time >= k * signal.T) and (time < signal.kw * signal.T + k * signal.T + signal.t1):
        return signal.A / (signal.kw * signal.T) * (time - k * signal.T - signal.t1)

    return -signal.A / (signal.T * (1.0 - signal.kw)) * (time - k * signal.T - signal.t1) + signal.A * (1.0 - signal.kw)


def unitStepFunction(signal, time):
    if time > signal.ts:
        return (time == signal.ts) and (0.5 * signal.A) or (signal.A)

    return 0


def unitImpulse(signal, time):
    if abs(time - signal.ts) > 1e-6:
        return complex(0.0, 0.0)

    return signal.A


def unitNoise(signal, time):
    return (signal.p > rng.random()) and (signal.A) or complex(0.0, 0.0)


class Function():
    def __init__(self, func, signal):
        self.__parts = [("add", func, self.__getParams(signal))]

    def __getParams(self, signal):
        params = Params(t1 = signal.t1, d = signal.d, T = signal.T, kw = signal.kw, ts = signal.ts, p = signal.p, f = signal.f)
        params.A = signal.A
        return params

    def __str___(self):
        text = "Function ["

        for v in self.__parts:
            text += str(v) + ", "

        return text[:-2] + "]"

    def __call__(self, _, time):
        value = complex(0.0, 0.0)

        for v in self.__parts:
            if v[0] == "add":
                value += v[1](v[2], time)

            elif v[0] == "sub":
                value -= v[1](v[2], time)

            elif v[0] == "mul":
                value *= v[1](v[2], time)

            elif v[0] == "div":
                value /= v[1](v[2], time)

        return value

    def isRandom(self):
        for v in self.__parts:
            if v[1] in (uniformDistributionNoise, gaussianNoise, unitNoise):
                return True

        return False

    def isDiscrete(self):
        for v in self.__parts:
            if type(v[1]) is Function:
                if not v[1].isDiscrete():
                    return False

            elif v[1] not in (unitImpulse, unitNoise):
                return False
        
        return True

    def add(self, func, signal):
        self.__parts.append(("add", func, self.__getParams(signal)))

    def sub(self, func, signal):
        self.__parts.append(("sub", func, self.__getParams(signal)))

    def mul(self, func, signal):
        self.__parts.append(("mul", func, self.__getParams(signal)))

    def div(self, func, signal):
        self.__parts.append(("div", func, self.__getParams(signal)))