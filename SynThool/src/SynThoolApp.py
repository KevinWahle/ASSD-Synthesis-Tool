from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHBoxLayout, QCheckBox, QSlider, QComboBox
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

from src.ui.windows.SynthesisTool_window import Ui_MainWindow
from src.MIDI.Midi import Midi

import numpy as np
import scipy.io.wavfile as wavfile

from src.synthesizers.KarplusSynth.karplus import KarplusStrongDrum, KarplusStrongGuitar
from src.synthesizers.sampleSynth.sample_synth import sample_synth

class SynThoolApp(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(SynThoolApp, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.isPlaying = False
        self.filename = ""
        self.tracks = np.empty((0, 2), dtype=object)    # [ track, on/off ]
        self.midi = None
        self.wav_data = None
        self.instruments = [    [ "Piano", "res/grand-piano.png", lambda n, v, t: sample_synth(n, v, t)[0] ],
                                [ "Guitarra", "res/guitar.png",  KarplusStrongGuitar],
                                [ "Platillo", "res/cymbals", KarplusStrongDrum ] ]
        self.playIcon = [QIcon("res/play.png"), QIcon("res/pause.png")]

        self.saveBtn.setEnabled(False)  # Deshabilitado hasta que se sintetice
        self.sinteziseBtn.setEnabled(False)  # Deshabilitado hasta que se cargue archivo
        self.playPauseBtn.setEnabled(False)  # Deshabilitado hasta que se sintetice
        self.stopBtn.setEnabled(False)  # Deshabilitado hasta que se sintetice
        self.songSlider.setEnabled(False)  # Deshabilitado hasta que se sintetice

        self.openBtn.clicked.connect(self.open_file)
        self.saveBtn.clicked.connect(self.saveFile)
        self.sinteziseBtn.clicked.connect(self.synthesize)
        self.playPauseBtn.clicked.connect(self.playPause)
        self.stopBtn.clicked.connect(self.stop)

        self.graficarBtn.clicked.connect(self.graphSpectrogram)

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

                self.tracks = np.empty(shape=(self.midi.amount_of_tracks, 2), dtype=object)    # [ track, on/off ]

                self.tracks[:, 0] = self.midi.tracks_midi_list
                self.tracks[:, 1] = True    # Por default todos activados

                self.showTracks()

                self.sinteziseBtn.setEnabled(True)
            except Exception as e:
                print("Error al interpretar el archivo: ", e)

    def showTracks(self):
        for i, track in enumerate(self.tracks[:, 0]):
            self.verticalLayout_4.addLayout(self.createTrackWidget(track, i))

    def createTrackWidget(self, track, i):
        layout = QHBoxLayout()
        # check = QCheckBox(track.name)
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

        try:

            for index, row in enumerate(self.verticalLayout_4.children()):
                checked = row.itemAt(0).widget().checkState() == QtCore.Qt.Checked
                # self.tracks[row.itemAt(0).widget().text()[-1], 1] = checked
                if (checked):
                    instrument = row.itemAt(1).widget().currentIndex()
                    volume = row.itemAt(2).widget().value()
                    self.midi.synthesize_track(index, self.getSynthFunc(instrument))
                    self.midi.wav_list[index] *= volume/100
                    print(index, checked, instrument, volume)

            self.wav_data = self.midi.weighTracks(self.midi.wav_list).astype(np.float32)

            self.isPlaying = False

            self.saveBtn.setEnabled(True)
            self.playPauseBtn.setEnabled(True)
            self.playPauseBtn.setIcon(self.playIcon[0])
            self.stopBtn.setEnabled(True)
            self.songSlider.setEnabled(True)

        except Exception as e:
            print("Error al sintetizar: ", e)

    def getSynthFunc(self, index):
        return self.instruments[index][2]

    def playPause(self):
        if self.isPlaying:  # Pausa
            self.isPlaying = False
            self.playPauseBtn.setIcon(self.playIcon[0])
        else:
            self.isPlaying = True
            self.playPauseBtn.setIcon(self.playIcon[1])

    def stop(self):
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


    def graphSpectrogram(self):
        print("Graficar espectrograma")