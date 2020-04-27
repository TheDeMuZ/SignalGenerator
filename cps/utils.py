# from numpy import arange
import pickle
from tkinter import filedialog

from .signal.signal import Signal


class FileNotChosenException(Exception):
    def __init__(self):
        super().__init__()


def signal_export(signal):
    filename = filedialog.asksaveasfilename()

    if filename == "":
        raise FileNotChosenException()
    
    with open(filename, "wb") as f:
        pickle.dump(signal, f, -1)


def signal_import():
    filename = filedialog.askopenfilename()

    if filename == "":
        raise FileNotChosenException()

    signal = None

    with open(filename, "rb") as f:
        signal = pickle.load(f)

    return signal


# def signal_export(signal):
#     isComplex = False

#     for v in signal.y_list:
#         if v.imag != 0:
#             isComplex = True
#             break

#     text = "t1: {}\nf: {}\ntyp: ".format(signal.t1, signal.f)

#     if isComplex:
#         text += "Zespolone\n"

#         for v in signal.y_list:
#             text += str(v) + "\n"

#     else:
#         text += "Rzeczywiste\n"

#         for v in signal.y_list:
#             text += str(v.real) + "\n"

#     filename = filedialog.asksaveasfilename()

#     if filename == "":
#         raise FileNotChosenException()
    
#     with open(filename, "w") as f:
#         f.write(text)


# def signal_import():
#     filename = filedialog.askopenfilename()

#     if filename == "":
#         raise FileNotChosenException()

#     text = None

#     with open(filename, "r") as f:
#         text = f.read().splitlines(False)

#     t1 = float(text[0][4:])
#     f = float(text[1][3:])
#     y_list = [complex(v) for v in text[3:]]
    
#     d = (len(y_list) - 1) / f
#     x_list = [float(v) for v in arange(t1, t1 + d + 1 / f, 1 / f)]

#     signal = Signal(t1 = t1, f = f, d = d)
#     signal.x_list = x_list
#     signal.y_list = y_list
#     signal.generate()
    
#     return signal