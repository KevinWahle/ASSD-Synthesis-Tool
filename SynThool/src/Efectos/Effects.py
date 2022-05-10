from scipy.io import wavfile
from scipy import signal
import numpy as np
import math
import matplotlib.pyplot as plt



# mysamplerate, data = wavfile.read('Efectos\Guirar_recorte.wav')


def echo (data, delay, decay, samplerate):  #delay in ms, decay in (0,1)
    if (data.ndim==1):
        data=np.array([data]).T
    delay=math.floor(delay/1000*samplerate)
    a=np.zeros(1)
    b=np.zeros(delay+1)
    b[0]=decay
    b[delay]=1
    a[0]=1
    for i in range(data.shape[1]):
        data[:, i]=signal.lfilter(b,a,data[:,i])

    return data.astype(np.int16)

def planeReverb (data, delay, decay, samplerate):   #delay in ms, decay in (0,1)
    if (data.ndim==1):
        data=np.array([data]).T
    delay=math.floor(delay/1000*samplerate)
    a=np.zeros(delay+1)
    b=np.zeros(1)
    b[0]=1
    a[delay]=decay
    a[0]=1
    for i in range(data.shape[1]):
        data[:, i]=signal.lfilter(b,a,data[:,i])
    return data.astype(np.int16)


def flanger (data, delay, decay, samplerate, fd=1): #delay in ms, decay in (0,1), fd in Hz (fd \approx 1)
    if (data.ndim==1):
        data=np.array([data]).T
    delay=math.floor(delay/1000*samplerate)
    flanger = np.zeros(data.shape)
    newDelay = np.ndarray(data.shape[0], dtype=int)

    for n in range(data.shape[0]):
        newDelay[n] = max(n - int(delay/2*(1-math.cos(2*np.pi*n*fd))), 0)
    print (newDelay)
    for i in range(data.shape[1]):
            flanger[:,i]=data[:,i]+decay * data[newDelay, i]

    return flanger.astype(np.int16)


def plotall (samplerate, data, mseg):   #Funcion de testeo
    length = data.shape[0] / samplerate
    time = np.linspace(0., length, data.shape[0])
    plt.plot(time, flanger(data, math.floor(mseg/1000*samplerate), 0.5, 1), label="flanger")
    plt.plot(time, data, label="input")
    plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()

# mseg1=200
# mseg2=10

# wavfile.write("echo.wav", mysamplerate, echo(data, mseg1, 0.5, mysamplerate))
# wavfile.write("planeReverb.wav", mysamplerate, planeReverb(data, mseg1, 0.5, mysamplerate))
# wavfile.write("flanger.wav", mysamplerate, flanger(data, mseg2, 0.5, mysamplerate, 0.9))