from scipy.io import wavfile
from scipy import signal
import numpy as np
import math
import matplotlib.pyplot as plt



#mysamplerate, data = wavfile.read('Guirar_recorte.wav')


def echo (data, delay, decay, samplerate):  #delay in ms, decay in (0,1)
    delay=math.floor(delay/1000*samplerate)
    a=np.zeros(1)
    b=np.zeros(delay+1)
    b[0]=decay
    b[delay]=1
    a[0]=1
    data=signal.lfilter(b,a,data[:,0])
    return data.astype(np.int16)

def planeReverb (data, delay, decay, samplerate):   #delay in ms, decay in (0,1)
    delay=math.floor(delay/1000*samplerate)
    a=np.zeros(delay+1)
    b=np.zeros(1)
    b[0]=1
    a[delay]=decay
    a[0]=1
    data=signal.lfilter(b,a,data[:,0])
    return data.astype(np.int16)


def flanger (data, delay, decay, samplerate, fd=1): #delay in ms, decay in (0,1), fd in Hz (fd \approx 1)
    delay=math.floor(delay/1000*samplerate)
    flanger = np.zeros(len(data[:,0]))
    for n in range(len(data[:,0])):
        newDelay=int(delay/2*(1-math.cos(n*fd)))
        flanger[n]=data[n][0]+decay*data[n-newDelay][0]
    return flanger.astype(np.int16)


def plotall (samplerate, data, mseg):   #Funcion de testeo
    length = data.shape[0] / samplerate
    time = np.linspace(0., length, data.shape[0])
    plt.plot(time, flanger(data, math.floor(mseg/1000*samplerate), 0.5), label="flanger")
    plt.plot(time, data[:, 1], label="input")
    plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()

mseg1=200
mseg2=10

#wavfile.write("echo.wav", mysamplerate, echo(data, mseg1, 0.5, mysamplerate))
#wavfile.write("planeReverb.wav", mysamplerate, planeReverb(data, mseg1, 0.5, mysamplerate))
#wavfile.write("flanger.wav", mysamplerate, flanger(data, mseg2, 0.5, mysamplerate, 1))