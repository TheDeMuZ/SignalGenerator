import math

from numpy import arange


def __rect(a):
    if abs(a) > 0.5:
        return 0

    elif abs(a) == 0.5:
        return 0.5
        
    return 1


def __tri(a):
    return (abs(a) < 1) and (1 - abs(a)) or 0


def __sinc(a):
    return (a == 0) and 1 or (math.sin(math.pi * a) / math.pi * a)


def pseudoAnalogSignal(signal):
    analog_x, analog_y = [], []

    T = 1.0 / signal.dac_f

    for time in arange(signal.t1, signal.t1 + signal.d + T, T):
        analog_x.append(time)
        analog_y.append(signal.function(None, time))

    return analog_x, analog_y


def zeroOrderHold(signal):
    analog_x, analog_y = [], []
    T = 1.0 / signal.dac_f

    for time in arange(signal.t1, signal.t1 + signal.d + T, T):
        value = complex(0.0, 0.0)
        t = time * signal.adc_f / signal.dac_f

        for i in range(len(signal.y_list)):
            re = signal.y_list[i].real * __rect(t / T + 0.5 - i)
            im = signal.y_list[i].imag * __rect(t / T + 0.5 - i)
            value += complex(re, im)
        
        analog_x.append(time)
        analog_y.append(value)

    return analog_x, analog_y


def firstOrderHold(signal):
    analog_x, analog_y = [], []
    T = 1.0 / signal.dac_f

    for time in arange(signal.t1, signal.t1 + signal.d + T, T):
        value = complex(0.0, 0.0)
        t = time * signal.adc_f / signal.dac_f

        for i in range(len(signal.y_list)):
            re = signal.y_list[i].real * __tri(t / T - i)
            im = signal.y_list[i].imag * __tri(t / T - i)
            value += complex(re, im)
        
        analog_x.append(time)
        analog_y.append(value)

    return analog_x, analog_y


def sincBasedReconstruction(signal):
    analog_x, analog_y = [], []
    T = 1.0 / signal.dac_f

    for time in arange(signal.t1, signal.t1 + signal.d + T, T):
        value = complex(0.0, 0.0)
        t = time * signal.adc_f / signal.dac_f

        for i in range(len(signal.y_list)):
            re = signal.y_list[i].real * __sinc(t / T - i)
            im = signal.y_list[i].imag * __sinc(t / T - i)
            value += complex(re, im)
        
        analog_x.append(time)
        analog_y.append(value)

    return analog_x, analog_y