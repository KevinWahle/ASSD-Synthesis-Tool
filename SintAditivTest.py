from functools import partial
from tabnanny import verbose
import SintAditiv as sa
import math
import numpy as np
import scipy.io.wavfile as wav # para wavesave
import matplotlib.pyplot as plt
import os 

def testADSR(): #Ok
    dur = 2; fs = 44100
    osc=sa.genSine(10, A=1, dur=dur, fs=fs, verbose=True)
    env=sa.adsrEnvelope([1, 0.1], [0.5, 0.2], [0.4,0.6], [0,0.1], dur=dur, fs=fs, verbose=True)
    x=np.linspace(0,dur,int(fs*dur))
    plt.plot(x,osc); plt.plot(x,env*osc)
    plt.show()

def partialMixerTest(): #Ok
    dur=2; fs=44100
    x=np.linspace(0,dur,int(fs*dur))
    adsr1 = {"A":[1, 0.1], "D":[0.5, 0.2], "S":[0.4,0.6], "R": [0,0.1]}
    adsr2 = {"A":[1, 0.2], "D":[0.25, 0.2], "S":[0.1,0.5], "R": [0,0.1]}
    mixed=sa.partialMixer([[100,0.75, adsr1],[500,0.25,adsr2]], dur=dur, fs=fs, verbose=False)
    plt.plot(x,mixed, label="Síntesis")
    plt.legend()
    plt.show()
    k = np.iinfo(np.int16).max          # Max de int16
    mixed=(k*mixed).astype(np.int16)    # La llevamos a la amplitud que trabaja int16 
    wav.write(filename="mixed.wav", rate=fs, data=mixed)

def genPartialsTest(): #ok
    # https://freewavesamples.com/
    # https://freepats.zenvoid.org/
    fs=44100
    instrument="Bass"; Note="C4"
    current_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_path, "res", "AddSynth", instrument + Note+".wav")
    sa.getPartials(path=path, filename= instrument + Note, fs=fs, verbose=True)

def loadPartialsTest(): #ok
    instrument="Bass"; Note="C4"

    #probamos la carga de partials
    partials=sa.loadPartials(instrument=instrument, note=Note)
    print(partials)

def test():             # Prueba completa SIN ADSR
    dur=1; fs=44100
    adsr = {"A":[1, 0.2], "D":[0.3, 0.2], "S":[0.25,0.5], "R": [0,0.1]}
    loadedpart=sa.loadPartials(instrument="Bass", note="C4")
    partials = [[part[0], part[1], adsr] for part in loadedpart]
    mixed=sa.partialMixer(partials, dur=dur, fs=fs, verbose=True)
    mixed/=np.max(mixed)
    k = np.iinfo(np.int16).max          # Max de int16
    mixed=(k*mixed).astype(np.int16)    # La llevamos a la amplitud que trabaja int16 
    wav.write(filename="mixed.wav", rate=fs, data=mixed)
