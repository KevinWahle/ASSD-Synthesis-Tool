from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHBoxLayout, QCheckBox, QSlider, QComboBox, QPushButton, QLabel, QLineEdit, QWidget, QMessageBox, QAction, QApplication
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

from src.ui.windows.SynthesisTool_window import Ui_MainWindow

import numpy as np
import mido


class SynThoolApp(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(SynThoolApp, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.isPlaying = False
        self.filename = ""
        self.tracks = np.ndarray((0, 2))    # [ track, on/off ]
        self.instruments = [    [ "Piano", "res/grand-piano.png" ],
                                [ "Guitarra", "res/guitar.png" ],
                                [ "Platillo", "res/cymbals" ] ]
        self.playIcon = [QIcon("res/play.png"), QIcon("res/pause.png")]

        self.saveBtn.setEnabled(False)  # Deshabilitado hasta que se sintetice
        self.sinteziseBtn.setEnabled(False)  # Deshabilitado hasta que se cargue archivo
        self.playPauseBtn.setEnabled(False)  # Deshabilitado hasta que se sintetice
        self.stopBtn.setEnabled(False)  # Deshabilitado hasta que se sintetice
        self.songSlider.setEnabled(False)  # Deshabilitado hasta que se sintetice

        self.openBtn.clicked.connect(self.open_file)
        self.sinteziseBtn.clicked.connect(self.synthesize)
        self.playPauseBtn.clicked.connect(self.playPause)
        self.stopBtn.clicked.connect(self.stop)

        self.graficarBtn.clicked.connect(self.graphSpectrogram)

    def open_file(self):
        self.filename, _ = QFileDialog.getOpenFileName(
                        None,
                        "Select File",
                        "",
                        "MIDI Files (*.mid);;All Files (*)",
                        )
        if self.filename:
            try:
                tracks = mido.MidiFile(self.filename).tracks

                self.tracks = np.ndarray((len(tracks), 2), dtype=object)

                self.tracks[:, 0] = tracks
                self.tracks[:, 1] = True    # Por default todos activados

                self.showTracks()

                self.sinteziseBtn.setEnabled(True)
            except Exception as e:
                print("Error al interpretar el archivo: ", e)

    def showTracks(self):
        for track in self.tracks[:, 0]:
            self.verticalLayout_4.addLayout(self.createTrackWidget(track))

    def createTrackWidget(self, track):
        layout = QHBoxLayout()
        check = QCheckBox(track.name)
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

            for row in self.verticalLayout_4.children():
                check = row.itemAt(0).widget().checkState()
                combo = row.itemAt(1).widget().currentIndex()
                slider = row.itemAt(2).widget().value()
                # print(check, combo, slider)

            self.saveBtn.setEnabled(True)
            self.playPauseBtn.setEnabled(True)
            self.playPauseBtn.setIcon(self.playIcon[0])
            self.stopBtn.setEnabled(True)
            self.songSlider.setEnabled(True)

        except Exception as e:
            print("Error al sintetizar: ", e)

    def playPause(self):
        if self.isPlaying:
            self.isPlaying = False
            self.playPauseBtn.setIcon(self.playIcon[0])
        else:	# Pausa
            self.isPlaying = True
            self.playPauseBtn.setIcon(self.playIcon[1])

    def stop(self):
        self.isPlaying = False
        self.playPauseBtn.setIcon(self.playIcon[0])
        self.songSlider.setValue(0)

    def graphSpectrogram(self):
        print("Graficar espectrograma")