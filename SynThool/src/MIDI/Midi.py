import mido
import numpy as np

######################################
######################################
######################################

def midinote2freq(n):
    A = 440  # Frecuencia de LA
    An = 69  # Valor correspondiente a LA440 en midi
    distance = abs(An - n)
    if n < An:
        return A * 2 ** (-distance / 12)
    else:
        return A * 2 ** (distance / 12)


def get_tempo(mid_):
    for msg in mid_:  # Search for tempo
        if msg.type == 'set_tempo':
            return msg.tempo


class Midi:
    def __init__(self, file_name, sample_rate = 44100):
        self.mid_object = None
        self.tracks_midi_list = None
        self.amount_of_tracks = 0
        self.file_name = file_name
        self.sample_rate = sample_rate
        self.wav_list = None
        self.sec_per_tick = 0
        self.duration_in_s = 0
        self.parserMidi()

    def parserMidi(self):
        self.mid_object = mido.MidiFile(self.file_name, clip=True)
        self.amount_of_tracks = len(self.mid_object.tracks)

        
        num_mess = []      # Sacando los duplicados, segun la documentacion
        dup = []

        for track in self.mid_object.tracks:
            if len(track) in num_mess:
                dup.append(track)
            else:
                num_mess.append(len(track))
        for track in dup:
            self.mid_object.tracks.remove(track)

        
        tracks_midi_list_dict = [[] for i in range(self.amount_of_tracks)]
        self.tracks_midi_list = [[] for i in range(self.amount_of_tracks)]

        for j, track in enumerate(self.mid_object.tracks):  # Solo las que tienen on y off 
            for i in track:
                if i.type == 'note_on' or i.type == 'note_off':
                    tracks_midi_list_dict[j].append(i.dict())
        
        for j, track in enumerate(tracks_midi_list_dict):   # Los tiempos que da midi son deltas, se pasan a absolutos
            time_data = 0.0
            for i in track:
                time = i['time'] + time_data
                i['time'] = time
                time_data = time
                if i['type'] == 'note_on' and i['velocity'] == 0:
                    i['type'] = 'note_off'
                # El formato queda [type, note, time, velocity, channel]
                message_data = []
                if i['type'] == 'note_on' or i['type'] == 'note_off':
                    message_data.append(i['type'])
                    message_data.append(i['note'])
                    message_data.append(i['time'])
                    message_data.append(i['velocity'])
                    message_data.append(i['channel'])
                    self.tracks_midi_list[j].append(message_data)

        self.tracks_midi_list = [x for x in self.tracks_midi_list if x != []]  # sacas las vacias
        self.amount_of_tracks = len(self.tracks_midi_list)
        self.duration_in_s = self.mid_object.length  # duration_in_s en segundos
        tempo = get_tempo(self.mid_object)  # Microsegundos por beat
        tempo_s = tempo / 1e6  # Segundos por beat
        self.sec_per_tick = tempo_s / self.mid_object.ticks_per_beat
        # self.wav_list = [np.zeros(int(self.sample_rate * self.duration_in_s)) for i in range(self.amount_of_tracks)] #lista de numpy arrays
        self.wav_list = [np.zeros((int(self.sample_rate * self.duration_in_s), 2)) for i in range(self.amount_of_tracks)]

    def synthesize_track(self, track, function):   #(note, vel, duration_in_s)
        self.wav_list[track] = np.zeros(self.wav_list[track].shape)
        for j, message_data in enumerate(self.tracks_midi_list[track]):
            if message_data[0] == 'note_on':
                A = message_data[3] 
                freq = midinote2freq(message_data[1])
                m = 1
                tick_start = message_data[2]    # format is [type, note, time, velocity, channel]
                while self.tracks_midi_list[track][j + m][0] != 'note off' and self.tracks_midi_list[track][j + m][1] != \
                        message_data[1]:
                    m += 1
                tick_end = self.tracks_midi_list[track][j + m][2]
                delta_ticks = tick_end - tick_start
                delta_t = delta_ticks * self.sec_per_tick
                n = int(self.sample_rate * tick_start * self.sec_per_tick)
                arr = function(message_data[1], A, delta_t)[0]
                wave = np.zeros((n, arr.shape[1]))
                wave = np.append(wave, arr, axis=0)
                if self.wav_list[track].shape[0] < wave.shape[0]:
                    wave = wave[:self.wav_list[track].shape[0]]
                else:
                    wave = np.append(wave, np.zeros((self.wav_list[track].shape[0] - wave.shape[0], wave.shape[1])), axis=0)
                self.wav_list[track] = np.add(self.wav_list[track], wave)
        maxVal = np.max(np.abs(self.wav_list[track]), axis=0)
        self.wav_list[track] /= np.maximum(1, maxVal)

    def weighTracks(self, midiArr):
        weighArr = np.sum(midiArr, axis=0)
        return weighArr / np.maximum(1, np.max(np.abs(weighArr), axis=0))

######################################
######################################
######################################


if __name__ == '__main__':

    from src.synthesizers.sampleSynth.sample_synth import sample_synth
    from scipy.io.wavfile import write

    synthBethoven = Midi('Beethoven-Moonlight-Sonata.mid')
    synthBethoven.synthesize_track(0, sample_synth)
    synthBethoven.synthesize_track(1, sample_synth)


    write("Beethoven.wav", 44100, synthBethoven.weighTracks(synthBethoven.wav_list).astype(np.float32))