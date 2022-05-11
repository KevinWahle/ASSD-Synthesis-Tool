#instalar intertools !!!!
#https://18alan.medium.com/
#https://www.noiiz.com/sounds/samples?instrument=27&sample_type=one_shot
#https://freewavesamples.com/sample-type/bass
from cProfile import label
import math
import numpy as np
from scipy.io import wavfile # para wavesave
import scipy.fft as fft
import scipy.signal as ss
import matplotlib.pyplot as plt
import os
import csv
import random as rd

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
    #release = genExp(S, [R[0],0.0001], samples(R))
    release = rectGen(S[0], R[0], samples(R))
    env= np.concatenate((attack, decay, sustain, release))

    if verbose: #Revisamo la envolvente
        x=np.linspace(0,dur,len(env))
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


        if sine.size < env.size:
            sine=np.append(sine,np.zeros(env.size-sine.size))
        elif sine.size > env.size:
            env=np.append(env,np.zeros(sine.size-env.size))
        
        sum+=sine*env

        if verbose:
            plt.plot(x,sine*env, label="Modulated"+str(round(partial[0],1))+"Hz")
            plt.legend()
            plt.show()

    sum/=max(sum)

    if True:
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
    peaks_index, _ = ss.find_peaks(data_fft, distance=np.argmax(data_fft)*0.05, height=data_fft[np.argmax(data_fft)]/20)

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
    current_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_path, "res", "AddSynth", instrument + note+"Partials.txt")
    csv_file = open(path)
    csv_reader = csv.reader(csv_file, delimiter='\t')      # Leemos el archivo 
    peaks=np.zeros((1,2))

    for line in csv_reader:
        peaks=np.concatenate((peaks, [[float(line[0]),float(line[1])]])) # Agregamos la data de todos los partials
    
    peaks=peaks[1:] #Borro el primer peak

    #peaks= [[peak1Freq,peak1Amp], [peak2Freq,peak2Amp], ...]
    return peaks

def calcADSRconst(f0, audio, fs=44100, verbose=False):
    
    #f0: Frecuencia del partial
    Ntot = len(audio)                              # Cant muestras audio
    t = np.linspace(0, Ntot/fs, Ntot)              # Generamos el vector de tiempo
    maxAudio=audio[np.argmax(audio)]


    ###### Calculo A
    A= [1, np.argmax(audio)/Ntot]

    # ###### Cálculo D
    # peaksIndex, _= ss.find_peaks(audio, distance= 2 * round(fs/f0), height=max(audio)/100)
    
    # peaks_val = np.array([audio[i] for i in peaksIndex])
    # peaks_t = np.array([t[i] for i in peaksIndex])
    # maxIndex = int(np.argmax(peaks_val))
    # max_peak = peaks_val[int(maxIndex)]
    
    # Dn = 0; Dni = 0

    # for i in range(maxIndex, len(peaksIndex)):
    #     tmax = peaks_t[maxIndex]
    #     peak_0 = peaks_val[i]; peak_1 = peaks_val[i+1]; peak_2 = peaks_val[i + 2]
    #     t_i = peaks_t[i]
    #     alfa = 0.1
        
    #     # El D es el punto en el que los picos empiezan a tener valores muy similares
    #     # Por eso la primera condición.
    #     if abs(peak_1 - peak_2) < alfa and 0.4*max_peak < peak_0 < 0.95*max_peak and tmax < t_i < 4*tmax:
    #         Dn = peaksIndex[i]
    #         Dni = i
    #         break

    # D= [audio[Dn]/maxAudio, Dn/Ntot] 

    # ###### Cálculo S

    # Sn = 0; Sni = 0; count = 0
    # D_peak = peaks_val[Dni]
    # try:
    #     for i in range(Dni, len(peaksIndex)):
    #         peak_prev = peaks_val[i-3]; peak_0 = peaks_val[i]; peak_1 = peaks_val[i+1]
    #         delta_m = abs(peak_prev - peak_0) # Delta previa al i-esimo pico
    #         delta_p = abs(peak_1 - peak_0)    # Delta a partir del i-esimo pico

    #         if delta_p > 0.1*abs(D_peak - peak_0) > delta_m and 0.4*max_peak > peak_0 > 0.2*max_peak:
    #             count += 1
    #             if count == 3:
    #                 Sn = peaksIndex[i]
    #                 Sni = i
    #                 break
    # except:
    #     Sni = 0
    #     i = 0
    #     while Sni < Dni:
    #         Sni = np.where(peaks_val <= 0.7*peaks_val[Dni])[0][i]
    #         i += 1
    #     Sn = peaksIndex[Sni]

    # S= [audio[Sn]/maxAudio, Sn/Ntot]

    # #### Calculo R
    # Rn=len(audio)-1
    # if len(peaksIndex[Sni:]) > 0:
    #     peaks=np.array(peaksIndex[Sni:])
    #     #Tomo la primer muestra que sea < max/100
    #     for index in peaksIndex[Sni:]:
    #         if audio[index]<maxAudio/50:
    #             Rn=index
    #             break
 
    # R= [0, Rn/Ntot]



    if verbose:
        plt.plot(t,audio, alpha=0.5)     
        plt.scatter(t[np.argmax(audio)], audio[np.argmax(audio)], marker="o", color="orange")
        plt.scatter(0.3, 0.27*maxAudio, marker="o", color="magenta")
        plt.scatter(0.62, 0.18*maxAudio, marker="o", color="red")
        plt.scatter(1.04, 0.067*maxAudio, marker="o", color="k")
        plt.show()

    return 0

def getADSR(instrument,note, fs=44100, verbose=False):
    
    current_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_path, "res", "AddSynth", instrument + note+".wav")

    samplerate, data = wavfile.read(path)
    data= data/np.iinfo(np.int16).max           # Normalizo la ampl del audio
    data=[el[0] for el in data]                 # Me quedo con uno de los canales
    Ntot = len(data)                            # Cant muestras audio
    dur = Ntot / samplerate 

    peaks = loadPartials(instrument=instrument, note=note)
    f0=peaks[np.argmax(peaks,axis=0)[1]][0]
    
    if verbose:
        data_fft = 2.0 / Ntot * np.abs(fft.fft(data)[1:Ntot // 2])  #Generamos el espectro del audio
        data_fft/=data_fft[np.argmax(data_fft)]
        freqs = fft.fftfreq(Ntot, 1 / fs)[1:Ntot // 2]    

    calcADSRconst(f0=f0, audio=data, fs=fs, verbose=True) # No funcionó

    if instrument=="Bass" and note=="C4":
        A = [1, 0.01]
        D = [0.427, 0.05]
        S = [0.3, 0.2]
        R = [0, 0.74]

    elif instrument=="Piano" and note=="C4":
        A = [1, 0.05]
        D = [0.783, 0.05]
        S = [0.629, 0.2]
        R = [0.0621, 0.7]
        
    elif instrument=="Cymbals" and note=="C2":
        A = [1, 0.05]
        D = [0.783, 0.05]
        S = [0.629, 0.2]
        R = [0.0621, 0.7]

    elif instrument=="Drum" and note=="":
        A = [1, 0.1]
        D = [0.18, 0.07]
        S = [0.068, 0.67]
        R = [0.005, 0.16]

    elif instrument=="Bell" and note=="C5":
        A = [1, 0.03]
        D = [0.27, 0.26]
        S = [0.18, 0.31]
        R = [0.067, 0.4]

    return A, D, S, R

def filterPartial(data, f0, peak, fs=44100, verbose=False):
    kp=0.3
    Wn=[(peak[0]-f0*kp), (peak[0]+f0*kp)]
    b,a=ss.cheby1(5, 1, Wn, btype='bandpass', analog=False, fs=fs)
    yout = ss.lfilter(b,a, data)


    if verbose:
        w,h=ss.freqz(b,a,fs=fs)
        plt.plot(w/(2*np.pi), h, label="Filtro"+str(peak[0]))
        plt.legend()
        plt.show() 

        t= np.linspace(0, len(data)/fs, len(data))
        plt.plot(t, yout, label="Salida"+str(peak[0]))
        plt.legend()
        plt.show() 
    
    return yout


#getADSR("Bell", "C5", verbose=True)