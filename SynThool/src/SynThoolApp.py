from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHBoxLayout, QCheckBox, QSlider, QComboBox
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

from src.ui.windows.SynthesisTool_window import Ui_MainWindow
from src.MIDI.Midi import Midi
from src.Efectos.Effects import echo, planeReverb, flanger

import numpy as np
import scipy.io.wavfile as wavfile
import sounddevice as sd

from src.synthesizers.KarplusSynth.karplus import KarplusStrongDrum, KarplusStrongGuitar
from src.synthesizers.sampleSynth.sample_synth import sample_synth

class SynThoolApp(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(SynThoolApp, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.isPlaying = False
        self.filename = ""
        # self.tracks = np.empty((0, 2), dtype=object)    # [ track, on/off ]
        self.midi = None
        self.wav_data = None
        self.instruments = [    [ "Piano", "res/grand-piano.png", lambda n, v, t: sample_synth(n, v, t)[0] ],
                                [ "Guitarra", "res/guitar.png",  KarplusStrongGuitar],
                                [ "Platillo", "res/cymbals", KarplusStrongDrum ] ]
        self.playIcon = [QIcon("res/play.png"), QIcon("res/pause.png")]

        self.verticalLayout_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.saveBtn.setEnabled(False)  # Deshabilitado hasta que se sintetice
        self.sinteziseBtn.setEnabled(False)  # Deshabilitado hasta que se cargue archivo
        self.playPauseBtn.setEnabled(False)  # Deshabilitado hasta que se sintetice
        self.stopBtn.setEnabled(False)  # Deshabilitado hasta que se sintetice
        self.songSlider.setEnabled(False)  # Deshabilitado hasta que se sintetice
        self.initialTime.setEnabled(False) # Deshabilitado hasta que se sintetice
        self.finalTime.setEnabled(False) # Deshabilitado hasta que se sintetice
        self.graficarBtn.setEnabled(False)  # Deshabilitado hasta que se sintetice

        self.openBtn.clicked.connect(self.open_file)
        self.saveBtn.clicked.connect(self.saveFile)
        self.sinteziseBtn.clicked.connect(self.synthesize)
        self.playPauseBtn.clicked.connect(self.playPause)
        self.stopBtn.clicked.connect(self.stop)

        self.graficarBtn.clicked.connect(self.graphSpectrogram)
        self.finalTime.timeChanged.connect(lambda time: self.initialTime.setMaximumTime(time))

    def open_file(self):
        self.filename, _ = QFileDialog.getOpenFileName(
                        None,
                        "Select File",
                        "",
                        "MIDI Files (*.mid);;All Files (*)")
        if self.filename:
            try:
                # tracks = mido.MidiFile(self.filename).tracks

                self.midi = Midi(self.filename)

                sd.default.samplerate = self.midi.sample_rate

                # toAdd = np.empty(shape=(self.midi.amount_of_tracks, 2), dtype=object)
                # toAdd[:, 0] = self.midi.tracks_midi_list
                # toAdd[:, 1] = True    # Por default todos activados

                self.createTracks()

                # self.tracks = np.concatenate((self.tracks, toAdd), axis=0)

                self.sinteziseBtn.setEnabled(True)
            except Exception as e:
                print("Error al interpretar el archivo: ", e)

    def createTracks(self):
        self.clearTracks()
        for i in range(self.midi.amount_of_tracks):
            self.verticalLayout_5.addLayout(self.createTrackWidget(i))

    def clearTracks(self):
        self.clearLayout(self.verticalLayout_5)

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())

    def createTrackWidget(self, i):
        layout = QHBoxLayout()
        check = QCheckBox('Track ' + str(i) + ': ')
        check.setChecked(True)
        check.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        slider = QSlider(QtCore.Qt.Horizontal)
        slider.setValue(100)
        combo = QComboBox()
        for item in self.instruments:
            combo.addItem(QIcon(item[1]), item[0])
        
        layout.addWidget(check)
        layout.addWidget(combo)
        layout.addWidget(slider)

        return layout

    def synthesize(self):

        self.isPlaying = False
        sd.stop()
        self.setPlaybackEnabled(False)
        self.initialTime.setEnabled(False)
        self.finalTime.setEnabled(False)
        self.graficarBtn.setEnabled(False)


        try:

            # visibles = np.empty(0, dtype=int)

            for index, row in enumerate(self.verticalLayout_5.children()):
                checked = row.itemAt(0).widget().checkState() == QtCore.Qt.Checked
                # self.tracks[index, 1] = checked

                if (checked):
                    instrument = row.itemAt(1).widget().currentIndex()
                    volume = row.itemAt(2).widget().value()
                    maxVol = row.itemAt(2).widget().maximum()
                    self.midi.synthesize_track(index, self.getSynthFunc(instrument))
                    self.midi.wav_list[index] = (volume/maxVol) * np.array(self.midi.wav_list[index])
    
                    # visibles = np.append(visibles, index)
                    # print(index, checked, instrument, volume)

            # tracks = self.tracks[visibles, 0]
            self.wav_data = self.midi.weighTracks(self.midi.wav_list).astype(np.float32)

            if self.reverbCheck.isChecked():
                delay = self.reverbRetrasoSlider.value()
                gain = self.reverbGananciaSlider.value()/100.
                self.wav_data = planeReverb(self.wav_data, delay, gain, self.midi.sample_rate)
            if self.echoCheck.isChecked():
                delay = self.ehcoRetrasoSlider.value()
                gain = self.echoGananciaSlider.value()/100.
                self.wav_data = echo(self.wav_data, delay, gain, self.midi.sample_rate)
            if self.flangerCheck.isChecked():
                delay = self.flangerRetrasoSlider.value()
                gain = self.flangerGananciaSlider.value()/100.
                freq = self.flangerFrecuenciaSlider.value()/1000.
                self.wav_data = flanger(self.wav_data, delay, gain, self.midi.sample_rate, freq)


        except Exception as e:
            print("Error al sintetizar: ", e)

        self.setPlaybackEnabled(True)
        self.playPauseBtn.setIcon(self.playIcon[0])
        
        duration = QtCore.QTime(0, 0).addSecs(int(len(self.wav_data) / self.midi.sample_rate))
        # print(duration.toString("mm:ss"))

        # self.initialTime.setMaximumTime(duration)     # No hace falta, se setea con la signal
        self.finalTime.setMaximumTime(duration)
        self.finalTime.setTime(duration)

        self.initialTime.setEnabled(True)
        self.finalTime.setEnabled(True)
        self.graficarBtn.setEnabled(True)

    def getSynthFunc(self, index):
        return self.instruments[index][2]

    def playPause(self):
        if self.isPlaying:  # Pausa
            self.isPlaying = False
            self.playPauseBtn.setIcon(self.playIcon[0])
        elif len(self.wav_data):
                sd.play(self.wav_data)

                self.isPlaying = True
                self.playPauseBtn.setIcon(self.playIcon[1])

    def stop(self):

        sd.stop()

        self.isPlaying = False
        self.playPauseBtn.setIcon(self.playIcon[0])
        self.songSlider.setValue(0)

    def saveFile(self):
        self.filename, _ = QFileDialog.getSaveFileName(
                        None,
                        "Save File",
                        "",
                        "WAV Files (*.wav);;All Files (*)")

        if self.filename:
            wavfile.write(self.filename, self.midi.sample_rate, self.wav_data)

    def setPlaybackEnabled(self, state):
        self.saveBtn.setEnabled(state)
        self.playPauseBtn.setEnabled(state)
        self.stopBtn.setEnabled(state)
        self.songSlider.setEnabled(state)

    def graphSpectrogram(self):
        self.widget1.clear()
        axes = self.widget1.axes
        init = int(-self.initialTime.time().secsTo(QtCore.QTime(0, 0)) * self.midi.sample_rate)
        end = int(-self.finalTime.time().secsTo(QtCore.QTime(0, 0)) * self.midi.sample_rate) + 1
        axes.specgram(self.wav_data[init:end, 0], NFFT=1024, Fs=self.midi.sample_rate)
        self.widget1.draw()