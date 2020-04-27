import math

from numpy import arange

import cps.converter.measures
from ..signal.signal import Signal


def __floor(a):
    return complex(math.floor(a.real), math.floor(a.imag))


def __distance(a, b):
    return ((a.real - b.real) ** 2 + (a.imag - b.imag) ** 2) ** 0.5


def __range(start, stop, step):
    values = []

    if step.real != 0.0:
        if step.imag != 0.0:
            for x in arange(start.real, stop.real, step.real):
                for y in arange(start.imag, stop.imag, step.imag):
                    values.append(complex(x, y))

        else:
            for x in arange(start.real, stop.real, step.real):
                values.append(complex(x, 0.0))

    elif step.imag != 0.0:
        for y in arange(start.imag, stop.imag, step.imag):
            values.append(complex(0.0, y))

    else:
        pass

    return values


def pseudoAnalogSignal(signal):
    analog_x, analog_y = [], []

    T = 0.001

    for time in arange(signal.t1, signal.t1 + signal.d + T, T):
        analog_x.append(time)
        analog_y.append(signal.function(None, time))

    return analog_x, analog_y


def evenSampling(signal):
    digital_x, digital_y = [], []

    T = 1.0 / signal.adc_f

    for time in arange(signal.t1, signal.t1 + signal.d + T, T):
        digital_x.append(time)
        digital_y.append(signal.function(None, time))

    return digital_x, digital_y


def roundedEvenQuantization(signal):
    _, analog_y = pseudoAnalogSignal(signal)
    quantized_x, quantized_y = [], []

    minA_re = abs(min([v.real for v in analog_y]))
    minA_im = abs(min([v.imag for v in analog_y]))

    maxA_re = abs(max([v.real for v in analog_y]))
    maxA_im = abs(max([v.imag for v in analog_y]))

    A_re = (minA_re > maxA_re) and (minA_re) or (maxA_re)
    A_im = (minA_im > maxA_im) and (minA_im) or (maxA_im)

    A = complex(A_re, A_im)
    q = A / (2 ** (signal.adc_bits - 1))

    T = 1.0 / signal.adc_f

    for time in arange(signal.t1, signal.t1 + signal.d + T, T):
        value = signal.function(None, time)

        possibleValues = __range(-A, A + q, q)
        minDistance = float("inf")
        targetValue = None

        for v in possibleValues:
            distance = __distance(value, v)

            if distance < minDistance:
                minDistance = distance
                targetValue = v

        quantized_x.append(time)
        quantized_y.append(targetValue)

    return quantized_x, quantized_y