import numpy as np
from src.MIDI.Midi import midinote2freq
import random as rand

def KarplusStrongGuitar(pitch, A, duration):
    f = midinote2freq(pitch)
    p = int((44100/f)-0.5)
    x = [rand.uniform(-1, 1) for _ in range(p)]

    x.append( x[0] / 0.5) # x[p] o x[N] según el paper, es mi primer y
    for n2 in range(p + 1, int(duration * 44100)):
        x.append(0.5 * (x[n2 - p] + x[n2 - p - 1]))

    Amplitude = A / 127
    out = Amplitude*np.array(x[p:])
    return out

def KarplusStrongDrum(pitch, A, duration):
    f = midinote2freq(pitch)
    p = int((44100/f)-0.5)
    x = []
    for n in range(p):
        x.append(rand.gauss(0,1)*A)

    for n2 in range(p+1, int(duration*44100)):
        d = rand.uniform(0,1)
        if d < 0.5:
            x.append(0.5*(x[n2-p]+x[n2-p-1]))
        else:
            x.append(-0.5 * (x[n2 - p] + x[n2 - p - 1]))

    maxX = max(x)
    for i in range(len(x)):
        x[i] = x[i]/maxX
    x /= 127
    return x[p:]