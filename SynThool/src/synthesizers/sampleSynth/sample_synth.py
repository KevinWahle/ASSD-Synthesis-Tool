from src.synthesizers.sampleSynth.sfzParser import load
from scipy.io.wavfile import read, write
import soundfile as sf                              
import numpy as np
# import os

PATH = 'src/synthesizers/sampleSynth/piano_samples/'

parsedSFZ = load(PATH + 'piano.sfz')

def linear_pitch_shift(data, ratio):
    """
    Pitch shift using linear interpolation
    """
    # ratio = 2 ** (delta_pitch / 12.)

    # Number of samples in the signal
    N = data.shape[0]
    # Number of samples in the signal after pitch shifting
    N_new = int(round(N / ratio))
    # Empty array for the new signal
    data_new = np.zeros((N_new, data.shape[1]))
    
    indexes_old = range(N)
    
    indexes_interp = np.linspace(0, N, N_new)
    
    # Linear interpolation
    for i in range(data.shape[1]):
        data_new[:, i] = np.interp(indexes_interp, indexes_old, data[:, i])

    return data_new

def sample_synth(note, vel, duration):

    regions = parsedSFZ['regions']

    region = None

    for reg in regions:
        if ('key' in reg and int(reg['key']) == note) or ( 'lokey' in reg and int(reg['lokey']) <= note and int(reg['hikey']) >= note):
            if ('hivel' in reg and int(reg['hivel']) >= vel) or ('lovel' in reg and int(reg['lovel']) <= vel):
                region = reg
                break

    # print(region)

    if region == None:
        print('Nota invalida: ', note)
        return np.array([]), 0

    sample = PATH + region['sample']

    # name = os.path.basename(sample).split('.')[0]

    data, sr = sf.read(sample)

    # print(data, sr, data.shape)

    if not 'ampeg_release' in region:
        region['ampeg_release'] = 0.001

    pitch_ratio = 1

    if 'pitch_keycenter' in region and note != int(region['pitch_keycenter']):
        diff = note - int(region['pitch_keycenter'])
        # print('diff: ', diff)
        pitch_ratio = 2 ** (diff / 12.)
    
    sound_len = int(np.ceil(duration * sr * pitch_ratio))

    rel_len = int(np.ceil(float(region['ampeg_release']) * sr * pitch_ratio))

    total_len = sound_len + rel_len

    sample_len = data.shape[0]

    if sample_len < total_len and region['loop_mode'] == 'loop_continuous':

        start = int(region['loop_start'])
        end = int(region['loop_end']) + 1

        loop_len = end - start

        reps = int(np.ceil((total_len - sample_len) / loop_len))

        loop = np.tile(data[start:end, :], (reps, 1))

        # print(loop, loop.shape)

        data = np.concatenate((data[:end, :], loop, data[end+1:, :]))


    if pitch_ratio != 1:
        # Se aplica el pitch shift
        data = linear_pitch_shift(data, pitch_ratio)
    
        # Se recalculan los tiempos de release
        sound_len = int(np.ceil(duration * sr))
        rel_len = int(np.ceil(float(region['ampeg_release']) * sr))

    # Se le aplica la atenuacion de release si es necesario
    data = apply_release(data, sound_len-1, rel_len)

    max = np.max(np.abs(data))

    data *= vel / (127. * max)

    # write(name + '_loop'+ str(int(loop_time)) + '.wav', sr, data.astype(np.float32))

    # print(data, sr, data.shape)

    # write(str(note) + '_' + str(int(duration)) + '.wav', sr, data.astype(np.float32))

    return data, sr

def apply_release(data, release_index, release_duration):
    
    nfinal = release_index + release_duration
    
    if release_duration > 0 and release_index >= 0 and nfinal <= data.shape[0]:

        data[release_index:nfinal, :] *= np.linspace(np.ones(data.shape[1]), np.zeros(data.shape[1]), release_duration)
        data = data[:nfinal, :]

    return data


if __name__ == '__main__':

    note = int(input('Escriba la nota: '))
    vel = int(input('Escriba la velocidad: '))
    duration = float(input('Escriba la duración: '))

    out = sample_synth(note, vel, duration)[0]

    print(out, out.shape)