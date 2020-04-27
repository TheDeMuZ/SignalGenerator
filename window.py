import cmath

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from cps.converter import adc, dac, measures
from cps.signal.signal import *
from cps.utils import *


class App():
    def __init__(self, root):
        self.root = root
        self.optionsTab = ttk.Notebook(root)

        self.signalTypes = [
            "Szum o rozkładzie jednostajnym",
            "Szum Gaussowski",
            "Sygnał sinusoidalny",
            "Sygnał sinusoidalny wyprostowany jednopołówkowo",
            "Sygnał sinusoidalny wyprostowany dwupołówkowo",
            "Sygnał prostokątny",
            "Sygnał prostokątny symetryczny",
            "Sygnał trójkątny",
            "Skok jednostkowy",
            "Impuls jednostkowy",
            "Szum impulsowy"
        ]

        self.paramNames = {
            "t1": "Czas początkowy (s):",
            "d": "Czas trwania sygnału (s):",
            "T": "Okres podstawowy (s):",
            "kw": "Współczynnik wypełnienia:",
            "ts": "Czas skoku (s):",
            "p": "Prawdopodobieństwo:",
            "f": "Częstotliwość próbkowania (Hz):"
        }

        self.param2Names = {
            "adc_f": "[A/C] Częstotliwość próbkowania (Hz):",
            "adc_bits": "[A/C] Liczba bitów konwertera:",
            "dac_f": "[C/A] Częstotliwość próbkowania (Hz):"
        }

        self.requiredParams = {
            "Szum o rozkładzie jednostajnym": "t1, d, f, A",
            "Szum Gaussowski": "t1, d, f, A",
            "Sygnał sinusoidalny": "t1, d, f, A, T",
            "Sygnał sinusoidalny wyprostowany jednopołówkowo": "t1, d, f, A, T",
            "Sygnał sinusoidalny wyprostowany dwupołówkowo": "t1, d, f, A, T",
            "Sygnał prostokątny": "t1, d, f, A, T, kw",
            "Sygnał prostokątny symetryczny": "t1, d, f, A, T, kw",
            "Sygnał trójkątny": "t1, d, f, A, T, kw",
            "Skok jednostkowy": "t1, d, f, A, ts",
            "Impuls jednostkowy": "t1, d, f, A, ts",
            "Szum impulsowy": "t1, d, f, A, p"
        }

        self.options = {
            "signalType": tk.StringVar(root),
            "A": {
                "re": tk.DoubleVar(root),
                "im": tk.DoubleVar(root)
            }, 
            "params": {
                "t1": tk.DoubleVar(root),
                "d": tk.DoubleVar(root),
                "T": tk.DoubleVar(root),
                "kw": tk.DoubleVar(root),
                "ts": tk.DoubleVar(root),
                "p": tk.DoubleVar(root),
                "f": tk.DoubleVar(root),
            },
            "params2": {
                "adc_f": tk.DoubleVar(root),
                "adc_bits": tk.IntVar(root),
                "dac_f": tk.DoubleVar(root)
            },
            "operation": tk.StringVar(root),
            "chosenSignal1": tk.StringVar(root),
            "chosenSignal2": tk.StringVar(root),
            "chosenSignalExport": tk.StringVar(root)
        }

        self.operationNames = [
            "Dodawanie",
            "Odejmowanie",
            "Mnożenie",
            "Dzielenie"
        ]

        self.operationLambdas = [
            lambda s1, s2 : s1 + s2,
            lambda s1, s2 : s1 - s2,
            lambda s1, s2 : s1 * s2,
            lambda s1, s2 : s1 / s2
        ]

        self.resultTab = ttk.Notebook(root)
        self.signalDict = {}

        tabControl = ttk.Notebook(root)
        
        self.optionsTab.configure(width = 400)
        self.optionsTab.pack(expand = False, fill = "y", side = "left")
        self.resultTab.pack(expand = True, fill = "both", side = "right")

        self.__initOptions()

    def __onButtonPress_NEW_SIGNAL(self):
        #########################
        ### SIGNAL GENERATION ###
        #########################
        try:
            A_re = self.options["A"]["re"].get()
            A_im = self.options["A"]["im"].get()
            signalType = self.options["signalType"].get()

            params = [v.get() for k, v in self.options["params"].items()]
            params2 = [v.get() for k, v in self.options["params2"].items()]

            signal = Signal(signalType, A_re, A_im, *params, *params2)
            signal.generate()

            self.__addSignalTab(signal)
            self.__refreshOptionMenus()

        except Exception:
            messagebox.showerror("Błąd", "Podano nieprawidłowe parametry!")

    def __onButtonPress_DO_OPERATION(self):
        #########################
        ### SIGNAL OPERATIONS ###
        #########################
        try:
            s1 = self.signalDict[self.options["chosenSignal1"].get()]
            s2 = self.signalDict[self.options["chosenSignal2"].get()]
            signal = None

            for i in range(len(self.operationNames)):
                if self.options["operation"].get() == self.operationNames[i]:
                    signal = self.operationLambdas[i](s1, s2)
                    break

            self.__addSignalTab(signal)
            self.__refreshOptionMenus()

        except FileNotChosenException:
            messagebox.showerror("Błąd", "Niekompatybilne sygnały!")

        except Exception:
            messagebox.showerror("Błąd", "Wystąpił błąd podczas operacji na sygnałach!")

    def __onButtonPress_IMPORT(self):
        # ####################
        # ## SIGNAL IMPORT ###
        # ####################
        try:
            signal = signal_import()
            self.__addSignalTab(signal)

        except FileNotChosenException:
            pass

        except Exception:
            messagebox.showerror("Błąd", "Wystąpił błąd podczas wczytywania sygnału!")

    def __onButtonPress_EXPORT(self):
        #####################
        ### SIGNAL EXPORT ###
        #####################
        try:
            signal = self.signalDict[self.options["chosenSignalExport"].get()]
            signal_export(signal)
            messagebox.showinfo("Sukces", "Sygnał został zapisany!")

        except FileNotChosenException:
            pass

        except Exception:
            messagebox.showerror("Błąd", "Wystąpił błąd podczas zapisywania sygnału!")

    def __refreshRequiredParams(self, event):
        self.label_required.configure(text = self.requiredParams[self.options["signalType"].get()])

    def __initSignalTypeView(self, parent):
        label = ttk.Label(parent, text = "Wybierz sygnał:")
        label.grid(column = 1, row = 1, sticky = "w")
        
        options = ttk.OptionMenu(parent, self.options["signalType"], self.signalTypes[0], *self.signalTypes, command = self.__refreshRequiredParams)
        options.configure(width = 60)
        options.grid(column = 1, row = 2, ipadx = 4, sticky = "w")

    def __initSignalParamsView(self, parent):
        ttk.Label(parent).grid(column = 1, row = 4)

        label_required = ttk.Label(parent, text = "Wymagane: ")
        label_required.grid(column = 1, row = 5, sticky = "w")

        self.label_required = ttk.Label(parent, text = "t1, d, f, A")
        self.label_required.grid(column = 1, row = 6, sticky = "w", padx = 10)

        ttk.Label(parent).grid(column = 1, row = 7)

        paramsLabel = ttk.Label(parent, text = "Parametry sygnału:")
        paramsLabel.grid(column = 1, row = 8, sticky = "w")

        label_A = ttk.Label(parent, text = "A - Amplituda: ")
        label_A.grid(column = 1, row = 9, sticky = "w", padx = 5)

        textBox_A_re = ttk.Entry(parent, textvariable = self.options["A"]["re"])
        textBox_A_re.grid(column = 1, row = 9, sticky = "w", padx = 135)

        textBox_A_im = ttk.Entry(parent, textvariable = self.options["A"]["im"])
        textBox_A_im.grid(column = 1, row = 9, sticky = "w", padx = 260)

        iter = 10

        for k, v in self.options["params"].items():
            label = ttk.Label(parent, text = k + " - " + self.paramNames[k])
            label.grid(column = 1, row = iter, sticky = "w", padx = 5)

            textBox = ttk.Entry(parent, textvariable = self.options["params"][k])
            textBox.grid(column = 1, row = iter, sticky = "w", padx = 200)
            iter += 1

        ttk.Label(parent).grid(column = 1, row = iter)

        converterLabel = ttk.Label(parent, text = "Parametry konwertera:")
        converterLabel.grid(column = 1, row = iter + 1, sticky = "w")
        
        iter += 2

        for k, v in self.options["params2"].items():
            label = ttk.Label(parent, text = self.param2Names[k])
            label.grid(column = 1, row = iter, sticky = "w", padx = 5)

            textBox = ttk.Entry(parent, textvariable = self.options["params2"][k])
            textBox.grid(column = 1, row = iter, sticky = "w", padx = 250)
            iter += 1

            label = ttk.Label(parent, text = k)
            label.grid(column = 1, row = iter, sticky = "e")

        ttk.Label(parent).grid(column = 1, row = iter)

        button = ttk.Button(parent, text = "Generuj sygnał", command = self.__onButtonPress_NEW_SIGNAL)
        button.grid(column = 1, row = iter + 1, sticky = "w", padx = 150)

    def __refreshOptionMenus(self):
        options = list(self.signalDict.keys())

        prev_chosenSignal1 = self.options["chosenSignal1"].get()
        prev_chosenSignal2 = self.options["chosenSignal2"].get()
        prev_chosenSignalExport = self.options["chosenSignalExport"].get()

        self.choice1.destroy()
        self.choice2.destroy()
        self.choiceExport.destroy()
        
        self.choice1 = ttk.OptionMenu(self.operationsFrame, self.options["chosenSignal1"], prev_chosenSignal1, *options)
        self.choice1.configure(width = 60)
        self.choice1.grid(column = 1, row = 5, ipadx = 4, sticky = "w")

        self.choice2 = ttk.OptionMenu(self.operationsFrame, self.options["chosenSignal2"], prev_chosenSignal2, *options)
        self.choice2.configure(width = 60)
        self.choice2.grid(column = 1, row = 8, ipadx = 4, sticky = "w")

        self.choiceExport = ttk.OptionMenu(self.ioFrame, self.options["chosenSignalExport"], prev_chosenSignalExport, *options)
        self.choiceExport.configure(width = 60)
        self.choiceExport.grid(column = 1, row = 2, ipadx = 4, sticky = "w")

    def __initOperationsView(self, parent):
        label_operation = ttk.Label(parent, text = "Wybierz operację:")
        label_operation.grid(column = 1, row = 1, sticky = "w")
        
        options = ttk.OptionMenu(parent, self.options["operation"], self.operationNames[0], *self.operationNames)
        options.configure(width = 60)
        options.grid(column = 1, row = 2, ipadx = 4, sticky = "w")

        ttk.Label(parent).grid(column = 1, row = 3)

        label_choice1 = ttk.Label(parent, text = "Wybierz pierwszą kartę:")
        label_choice1.grid(column = 1, row = 4, sticky = "w")
        
        self.choice1 = ttk.OptionMenu(parent, self.options["chosenSignal1"], "<Wybierz kartę>")
        self.choice1.configure(width = 60)
        self.choice1.grid(column = 1, row = 5, ipadx = 4, sticky = "w")

        ttk.Label(parent).grid(column = 1, row = 6)

        label_choice2 = ttk.Label(parent, text = "Wybierz drugą kartę:")
        label_choice2.grid(column = 1, row = 7, sticky = "w")
        
        self.choice2 = ttk.OptionMenu(parent, self.options["chosenSignal2"], "<Wybierz kartę>")
        self.choice2.configure(width = 60)
        self.choice2.grid(column = 1, row = 8, ipadx = 4, sticky = "w")

        ttk.Label(parent).grid(column = 1, row = 9)

        button = ttk.Button(parent, text = "Wykonaj operację", command = self.__onButtonPress_DO_OPERATION)
        button.grid(column = 1, row = 10, sticky = "w", padx = 150)

    def __initInputOutputView(self, parent):
        label_choiceExport = ttk.Label(parent, text = "Wybierz sygnał do zapisania:")
        label_choiceExport.grid(column = 1, row = 1, sticky = "w")
        
        self.choiceExport = ttk.OptionMenu(parent, self.options["chosenSignalExport"], "<Wybierz kartę>")
        self.choiceExport.configure(width = 60)
        self.choiceExport.grid(column = 1, row = 2, ipadx = 4, sticky = "w")

        ttk.Label(parent).grid(column = 1, row = 3)

        button = ttk.Button(parent, text = "Zapisz sygnał", command = self.__onButtonPress_EXPORT)
        button.grid(column = 1, row = 4, sticky = "w", padx = 150)

        ttk.Label(parent).grid(column = 1, row = 5)

        button = ttk.Button(parent, text = "Wczytaj signał", command = self.__onButtonPress_IMPORT)
        button.grid(column = 1, row = 6, sticky = "w", padx = 147.5)

    def __initOptions(self):
        ###############
        ### mainTab ###
        ###############
        mainTab = ttk.Notebook(self.root)
        self.optionsTab.add(mainTab, text = "Generuj sygnał")

        mainFrame = ttk.Frame(mainTab)
        mainFrame.pack(expand = True, fill = "both")

        self.__initSignalTypeView(mainFrame)
        self.__initSignalParamsView(mainFrame)

        #####################
        ### operationsTab ###
        #####################
        operationsTab = ttk.Notebook(self.root)
        self.optionsTab.add(operationsTab, text = "Operacje")

        operationsFrame = ttk.Frame(operationsTab)
        operationsFrame.pack(expand = True, fill = "both")

        self.__initOperationsView(operationsFrame)

        #############
        ### ioTab ###
        #############
        ioTab = ttk.Notebook(self.root)
        self.optionsTab.add(ioTab, text = "Więcej")

        ioFrame = ttk.Frame(ioTab)
        ioFrame.pack(expand = True, fill = "both")

        self.__initInputOutputView(ioFrame)

        #########################
        ### fields assignment ###
        #########################
        self.mainFrame = mainFrame
        self.operationsFrame = operationsFrame
        self.ioFrame = ioFrame

    def __addChart(self, parent, x_list, y_list, side, title, isDottedChart = False):
        f = Figure(figsize = (1, 1), dpi = 100)
        a = f.add_subplot()
        a.set_title(title)

        if isDottedChart:
            a.plot(x_list, y_list, marker = ".", linestyle = "None")

        else:
            a.plot(x_list, y_list)

        canvas = FigureCanvasTkAgg(f, parent)
        canvas.get_tk_widget().pack(expand = True, fill = "both", side = side)

        return a

    def __addDottedChart(self, parent, x_list, y_list, side, title):
        self.__addChart(parent, x_list, y_list, side, title, True)

    def __addHistogram(self, parent, y_list, side, title, compartments):
        f = Figure(figsize = (1, 1), dpi = 100)
        a = f.add_subplot()
        a.set_title(title)
        
        _, _, patches = a.hist(y_list, bins = compartments)

        for i in range(len(patches)):
            value = int((i / len(patches) * 0.8 + 0.1) * 0xff)            
            color = "#{0:02x}{0:02x}ff".format(value)
            patches[i].set_facecolor(color)

        canvas = FigureCanvasTkAgg(f, parent)
        canvas.get_tk_widget().pack(expand = True, fill = "both", side = side)

    def __addParameterLabels(self, parent, signal):
        ttk.Label(parent).grid(column = 1, row = 1)

        label_averageValue = ttk.Label(parent, text = "Wartość średnia sygnału: " + str(signal.averageValue).replace("j", "i").replace("+", " + "))
        label_averageValue.grid(column = 1, row = 2, sticky = "w", padx = 20)

        label_absoluteAverageValue = ttk.Label(parent, text = "Wartość średnia bezwzględna sygnału: " + str(signal.absoluteAverageValue).replace("j", "i").replace("+", " + "))
        label_absoluteAverageValue.grid(column = 1, row = 3, sticky = "w", padx = 20)

        label_averagePower = ttk.Label(parent, text = "Moc średnia sygnału: " + str(signal.averagePower).replace("j", "i").replace("+", " + "))
        label_averagePower.grid(column = 1, row = 4, sticky = "w", padx = 20)

        label_varianceAroundTheAverageValue = ttk.Label(parent, text = "Wariancja sygnału wokół wartości średniej: " + str(signal.varianceAroundTheAverageValue).replace("j", "i").replace("+", " + "))
        label_varianceAroundTheAverageValue.grid(column = 1, row = 5, sticky = "w", padx = 20)

        label_effectiveValue = ttk.Label(parent, text = "Wartość skuteczna sygnału: " + str(signal.effectiveValue).replace("j", "i").replace("+", " + "))
        label_effectiveValue.grid(column = 1, row = 6, sticky = "w", padx = 20)

    def __fillHistogramTab(self, parent, x_list, y_list_re, y_list_im):
        for i in range(1, 5):
            frame = ttk.Frame(parent)
            self.__addHistogram(frame, y_list_re, "top", "Wartości rzeczywiste", i * 5)
            self.__addHistogram(frame, y_list_im, "bottom", "Wartości zespolone", i * 5)
            parent.add(frame, text = str(i * 5) + " przedziałów")

    def __fillGenerationTab(self, parent, signal):
        signalTab = ttk.Notebook(parent)

        dotted = (signal.function and signal.function.isDiscrete())

        #################
        ### chartTab1 ###
        #################
        chartTab1 = ttk.Frame(parent)
        signalTab.add(chartTab1, text = "Wykresy wartości")

        x = signal.x_list
        y_re = [v.real for v in signal.y_list]
        y_im = [v.imag for v in signal.y_list]

        if dotted:
            chart_re = self.__addDottedChart(chartTab1, x, y_re, "top", "Wartości rzeczywiste")
            chart_im = self.__addDottedChart(chartTab1, x, y_im, "bottom", "Wartości zespolone")

        else:
            chart_re = self.__addChart(chartTab1, x, y_re, "top", "Wartości rzeczywiste")
            chart_im = self.__addChart(chartTab1, x, y_im, "bottom", "Wartości zespolone")

        #################
        ### chartTab2 ###
        #################
        chartTab2 = ttk.Frame(parent)
        signalTab.add(chartTab2, text = "Wykresy modułu i fazy")

        y_mod = [abs(v) for v in signal.y_list]
        y_phase = [cmath.phase(v) for v in signal.y_list]

        if dotted:
            chart_mod = self.__addDottedChart(chartTab2, x, y_mod, "top", "Moduł")
            chart_phase = self.__addDottedChart(chartTab2, x, y_phase, "bottom", "Faza")

        else:
            chart_mod = self.__addChart(chartTab2, x, y_mod, "top", "Moduł")
            chart_phase = self.__addChart(chartTab2, x, y_phase, "bottom", "Faza")

        ####################
        ### histogramTab ###
        ####################
        histogramTab = ttk.Notebook(parent)
        signalTab.add(histogramTab, text = "Histogramy")

        self.__fillHistogramTab(histogramTab, x, y_re, y_im)

        #####################
        ### parametersTab ###
        #####################
        parametersTab = ttk.Frame(parent)
        signalTab.add(parametersTab, text = "Parametry")
        self.__addParameterLabels(parametersTab, signal)

        signalTab.pack(expand = True, fill = "both")

    def __addConverterParamsTab(self, paramsFrame, analog_y, digital_y, i = 1, padx = 20):
        ttk.Label(paramsFrame).grid(column = 1, row = i)

        MSE = measures.meanSquaredError(analog_y, digital_y)
        label_MSE = ttk.Label(paramsFrame, text = "Błąd średniokwadratowy: " + str(MSE).replace("j", "i").replace("+", " + "))
        label_MSE.grid(column = 1, row = i + 1, sticky = "w", padx = padx)

        SNR = measures.signalToNoiseRatio(analog_y, digital_y)
        label_SNR = ttk.Label(paramsFrame, text = "Stosunek sygnał-szum: " + str(SNR).replace("j", "i").replace("+", " + "))
        label_SNR.grid(column = 1, row = i + 2, sticky = "w", padx = padx)

        MD = measures.maximumDifference(analog_y, digital_y)
        label_MD = ttk.Label(paramsFrame, text = "Maksymalna różnica: " + str(MD).replace("j", "i").replace("+", " + "))
        label_MD.grid(column = 1, row = i + 3, sticky = "w", padx = padx)

        ENOB = measures.effectiveNumberOfBits(analog_y, digital_y)
        label_ENOB = ttk.Label(paramsFrame, text = "Efektywna liczba bitów: " + str(ENOB).replace("j", "i").replace("+", " + "))
        label_ENOB.grid(column = 1, row = i + 4, sticky = "w", padx = padx)
        
        return i + 4

    def __fillADConverterTab(self, parent, signal):
        signalTab = ttk.Notebook(parent)
        signalTab.pack(expand = True, fill = "both")

        ################
        ### SAMPLING ###
        ################
        samplingTab = ttk.Notebook(signalTab)
        signalTab.add(samplingTab, text = "Próbkowanie równomierne")

        ax, ay = adc.pseudoAnalogSignal(signal)
        sx, sy = adc.evenSampling(signal)

        a_re = self.__addChart(samplingTab, ax, [v.real for v in ay], "top", "Wartości rzeczywiste")
        a_re.plot(sx, [v.real for v in sy], marker = ".", linestyle = "None")

        a_im = self.__addChart(samplingTab, ax, [v.imag for v in ay], "bottom", "Wartości zespolone")
        a_im.plot(sx, [v.imag for v in sy], marker = ".", linestyle = "None")

        if signal.adc_bits > 0:
            ####################
            ### QUANTIZATION ###
            ####################
            quantizationTab = ttk.Notebook(signalTab)
            signalTab.add(quantizationTab, text = "Kwantyzacja równomierna z zaokrągleniem")

            qx, qy = adc.roundedEvenQuantization(signal)

            a_re = self.__addChart(quantizationTab, ax, [v.real for v in ay], "top", "Wartości rzeczywiste")
            a_re.plot(qx, [v.real for v in qy])

            a_im = self.__addChart(quantizationTab, ax, [v.imag for v in ay], "bottom", "Wartości zespolone")
            a_im.plot(qx, [v.imag for v in qy])

            ################
            ### MEASURES ###
            ################
            measuresTab = ttk.Notebook(signalTab)
            signalTab.add(measuresTab, text = "Miary błędu kwantyzacji")

            paramsFrame = ttk.Frame(measuresTab)
            paramsFrame.pack(expand = True, fill = "both")
            self.__addConverterParamsTab(paramsFrame, ay, qy)

            return qx, qy

        return None, None

    def __fillDAConverterTab(self, parent, signal, digital_x, digital_y):
        signalTab = ttk.Notebook(parent)
        signalTab.pack(expand = True, fill = "both")

        digital = Signal(t1 = signal.t1, d = signal.d, f = signal.dac_f, adc_f= signal.adc_f, dac_f = signal.dac_f)
        digital.x_list = digital_x
        digital.y_list = digital_y

        ax, ay = dac.pseudoAnalogSignal(signal)

        ###########
        ### ZOH ###
        ###########
        zohTab = ttk.Notebook(signalTab)
        signalTab.add(zohTab, text = "ZOH")

        a1_x, a1_y = dac.zeroOrderHold(digital)

        a_re = self.__addChart(zohTab, ax, [v.real for v in ay], "top", "Wartości rzeczywiste")
        a_re.plot(a1_x, [v.real for v in a1_y])

        a_im = self.__addChart(zohTab, ax, [v.imag for v in ay], "bottom", "Wartości zespolone")
        a_im.plot(a1_x, [v.imag for v in a1_y])

        ###########
        ### FOH ###
        ###########
        fohTab = ttk.Notebook(signalTab)
        signalTab.add(fohTab, text = "FOH")

        a2_x, a2_y = dac.firstOrderHold(digital)

        a_re = self.__addChart(fohTab, ax, [v.real for v in ay], "top", "Wartości rzeczywiste")
        a_re.plot(a2_x, [v.real for v in a2_y])

        a_im = self.__addChart(fohTab, ax, [v.imag for v in ay], "bottom", "Wartości zespolone")
        a_im.plot(a2_x, [v.imag for v in a2_y])

        ############
        ### SINC ###
        ############
        sincTab = ttk.Notebook(signalTab)
        signalTab.add(sincTab, text = "SINC")

        a3_x, a3_y = dac.sincBasedReconstruction(digital)

        a_re = self.__addChart(sincTab, ax, [v.real for v in ay], "top", "Wartości rzeczywiste")
        a_re.plot(a3_x, [v.real for v in a3_y])

        a_im = self.__addChart(sincTab, ax, [v.imag for v in ay], "bottom", "Wartości zespolone")
        a_im.plot(a3_x, [v.imag for v in a3_y])

        ################
        ### MEASURES ###
        ################
        measuresTab = ttk.Notebook(signalTab)
        signalTab.add(measuresTab, text = "Miary błędu rekonstrukcji")

        paramsFrame = ttk.Frame(measuresTab)
        paramsFrame.pack(expand = True, fill = "both")
        
        ttk.Label(paramsFrame).grid(column = 1, row = 1)

        zohLabel = ttk.Label(paramsFrame, text = "ZOH:")
        zohLabel.grid(column = 1, row = 2, sticky = "w", padx = 20)
        i = self.__addConverterParamsTab(paramsFrame, a1_y, signal.y_list, 2, 40)

        ttk.Label(paramsFrame).grid(column = 1, row = i + 1)

        zohLabel = ttk.Label(paramsFrame, text = "FOH:")
        zohLabel.grid(column = 1, row = i + 2, sticky = "w", padx = 20)
        i = self.__addConverterParamsTab(paramsFrame, a2_y, signal.y_list, i + 2, 40)
        
        ttk.Label(paramsFrame).grid(column = 1, row = i + 1)

        sincLabel = ttk.Label(paramsFrame, text = "SINC:")
        sincLabel.grid(column = 1, row = i + 2, sticky = "w", padx = 20)
        self.__addConverterParamsTab(paramsFrame, a3_y, signal.y_list, i + 2, 40)

    def __addSignalTab(self, signal):
        masterTab = ttk.Notebook(self.root)

        generationTab = ttk.Notebook(masterTab)
        self.__fillGenerationTab(generationTab, signal)
        masterTab.add(generationTab, text = "Generacja")

        if not signal.function or not signal.function.isRandom():
            if signal.adc_f > 0:
                adcTab = ttk.Notebook(masterTab)
                digital_x, digital_y = self.__fillADConverterTab(adcTab, signal)
                masterTab.add(adcTab, text = "A/C")

                if signal.dac_f > 0:
                    dacTab = ttk.Notebook(masterTab)
                    self.__fillDAConverterTab(dacTab, signal, digital_x, digital_y)
                    masterTab.add(dacTab, text = "C/A")

        tabName = "Sygnał " + str(len(self.signalDict) + 1)
        self.signalDict[tabName] = signal
        self.resultTab.add(masterTab, text = tabName)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Zadanie 2")
    root.minsize(800, 600)
    root.maxsize(1600, 900)

    App(root)
    root.mainloop()