from signal import signal
from scipy.io import wavfile as wave
import scipy.signal as sig
import matplotlib.pyplot as plt



# f_s: frecuencia de sampleo, window_u: ventana, nperseg_u: numero de multiplos de ventana, 
# nfft_u: numero de multiplos de ventana, noverlap_u: porcentaje de overlap
def spectogram(f_s, data, window_u, nperseg_u, noverlap_u, nfft_u): 


    data_size = len( data.shape )

    MONO = 1
    STEREO = 2

    if data_size == MONO:
        f,t,spec= sig.spectrogram(data,fs=f_s,window=window_u,nperseg=nperseg_u,noverlap=noverlap_u,nfft=nfft_u)
    elif data_size == STEREO:
        f_1,t_1,spec_1 =sig.spectrogram(data[:,0],fs=f_s,window=window_u,nperseg=nperseg_u,noverlap=noverlap_u,nfft=nfft_u)
        f_2,t_2,spec_2 =sig.spectrogram(data[:,1],fs=f_s,window=window_u,nperseg=nperseg_u,noverlap=noverlap_u,nfft=nfft_u)
        f = f_1
        t = t_1
        spec = 0.5*(spec_1+spec_2)

    plt.pcolormesh(t, f, spec)
    plt.title("Espectrograma")
    plt.xlabel("t(seg)")
    plt.ylabel("f(Hz)")
    plt.ylim(top=f[-1])
    plt.xlim(right=t[-1])
    plt.show()

#Ejemplo
# f_s, file = wave.read('G#3.wav')

# window_u = 'bartlett'
# nperseg_u = None
# nfft_u = None
# noverlap_u = 50

# spectogram(f_s, file, window_u, nperseg_u, noverlap_u, nfft_u)