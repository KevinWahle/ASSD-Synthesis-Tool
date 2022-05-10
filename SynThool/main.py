import sys
from PyQt5.QtWidgets import QApplication
from src.SynThoolApp import SynThoolApp

app = QApplication(sys.argv)
win = SynThoolApp()
win.show()
sys.exit(app.exec())