#instalar intertools !!!!
#https://18alan.medium.com/
from cProfile import label
import math
import numpy as np
from scipy.io import wavfile # para wavesave
import scipy.fft as fft
import scipy.signal as ss
import matplotlib.pyplot as plt
import os
import csv

def genSine(freq, A=1, phase=0, fs=44100, dur=1, verbose=False):
    phase = (phase / 360) * 2 * math.pi     # convert phase to radians
    t = np.linspace(0,dur,int(fs*dur))
    sine = A*np.sin(phase + 2 * math.pi * freq * t)
    if verbose:
        plt.plot(t,sine, label="Sine"+str(round(freq,3))+"Hz")
        plt.legend()
        plt.show()
    return sine

def genExp(prev, next, samples):
    # Genera una exponencial entre dos puntos de dos etapas.
    # exp= k*e^(at)
    a=math.log(next[0]/prev[0])/ next[1]
    k=next[0]/math.exp(a*next[1])
    return k*np.exp(a*np.linspace(0, next[1], samples))

def adsrEnvelope( A, D, S, R, dur=1, fs=44100, verbose=False):
# Cada etapa contiene A=[nivel, duracion]
# nivel es el valor con el que termina, duracion es lo que dura esa etapa con respecto al total
    rectGen = lambda init, end, samples: np.linspace(init, end, samples)
    samples= lambda K: int(dur*K[1]*fs)

    # calculo de la moduladora
    attack = rectGen(0, A[0], samples(A))
    decay = rectGen(A[0], D[0], samples(D))
    sustain = rectGen(D[0], S[0], samples(S))
    release = genExp(S, [0.1,0.0001], samples(R))
    #release = rectGen(S[0], R[0], samples(R))
    env= np.concatenate((attack, decay, sustain, release))

    if verbose: #Revisamo la envolvente
        x=np.linspace(0,dur,int(fs*dur))
        plt.plot(x,env, label="Moduladora")
        plt.legend()
        plt.show()

    return env

def partialMixer(partials, dur=1, fs=44100, verbose=False):
    sum=np.zeros(int(dur*fs))
    x=np.linspace(0,dur,int(fs*dur))

    for partial in partials:
        sine=genSine(freq=partial[0], A=partial[1], fs=fs, dur=dur, verbose=verbose)
        env = adsrEnvelope(A=partial[2]["A"], D=partial[2]["D"], S=partial[2]["S"], R=partial[2]["R"], dur=dur, fs=fs, verbose=verbose)
        sum+=sine*env

        if verbose:
            plt.plot(x,sine*env, label="Modulated"+str(round(partial[0],1))+"Hz")
            plt.legend()
            plt.show()

    if verbose:
        plt.plot(x,sum, label="Sum")
        plt.legend()
        plt.show()
    return sum  

def saveAsWav(audio, fname="temp.wav", vol=1, fs=44100):
    k = np.iinfo(np.int16).max          # Max de int16
    audio = (audio * vol * k).astype(np.int16)    # La llevamos a la amplitud que trabaja int16 
    wavfile.write(filename=fname, rate=fs, data=audio)

def getPartials(path, filename, fs, verbose=False):

    samplerate, data = wavfile.read(path)
    data= data/np.iinfo(np.int16).max           # Normalizo la ampl del audio
    data=[el[0] for el in data]                 # Me quedo con uno de los canales
    Ntot = len(data)                            # Cant muestras audio
    dur = Ntot / samplerate 
    
    #TODO: Revisar la fft
    data_fft = 2.0 / Ntot * np.abs(fft.fft(data)[1:Ntot // 2])  #Generamos el espectro del audio
    data_fft/=data_fft[np.argmax(data_fft)]
    freqs = fft.fftfreq(Ntot, 1 / fs)[1:Ntot // 2]
    f0 = freqs[np.argmax(data_fft)]
    peaks_index, _ = ss.find_peaks(data_fft, distance=np.argmax(data_fft)*0.98, height=data_fft[np.argmax(data_fft)]/100)

    #peaks= [[peak1Amp,peak1Freq], [peak2Amp,peak2Freq], ...]
    peaks=np.zeros((1,2))

    for index in peaks_index:   #Guardamos los peaks
        el = np.array([[freqs[index],data_fft[index]]])
        peaks=np.concatenate((peaks, el))
    
    peaks=peaks[1:] #Borro el primer peak

    if verbose:
        plt.plot(freqs,data_fft)        # Espectro
        x=[peak[0] for peak in peaks]   # arreglo de frec
        y=[peak[1] for peak in peaks]   # arreglo de ampl
        plt.scatter(x, y, marker="x", color="orange")
        plt.show()

    current_path = os.path.dirname(os.path.abspath(__file__))
    targetpath = os.path.join(current_path, "res", "AddSynth", filename+"Partials.txt")
    f = open(targetpath, "w+")
    
    for freq, amp in peaks: # Guardamos la data en un archivo
        f.write(str(freq) + "\t" + str(amp) + "\n")
    f.close()

def loadPartials(instrument, note):
    csv_file = open("res/AddSynth/"+instrument+note+"Partials.txt")
    csv_reader = csv.reader(csv_file, delimiter='\t')      # Leemos el archivo 
    peaks=np.zeros((1,2))

    for line in csv_reader:
        peaks=np.concatenate((peaks, [[float(line[0]),float(line[1])]])) # Agregamos la data de todos los partials
    
    peaks=peaks[1:] #Borro el primer peak

    #peaks= [[peak1Freq,peak1Amp], [peak2Freq,peak2Amp], ...]
    return peaks

def getADSR(filename):
    pass
