# ------------------------------------------------------
# -------------------- PlotWidget.py --------------------
# ------------------------------------------------------
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFileDialog, QToolButton, QWidget, QVBoxLayout

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT

import csv
from src.ui.widgets.LabelEditWidget import LabelEditWidget
# from LabelEditWidget import LabelEditWidget

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        #  Create widgets
        self.canvas = FigureCanvas(Figure(constrained_layout=True))
        self.axes = self.canvas.figure.subplots()
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        # self.canvas.figure.tight_layout()

        # Add widgets to toolbar
            # Export to CSV Widget
        self.btnExport = QToolButton()
        self.btnExport.setIcon(QIcon("res/csv.png"))
        self.toolbar.insertWidget(self.toolbar.actions()[len(self.toolbar.actions())-1], self.btnExport)
            # Labeledit Widget
        self.labelEdit = LabelEditWidget()
        self.toolbar.insertSeparator(self.toolbar.actions()[len(self.toolbar.actions())-1])
        self.toolbar.insertWidget(self.toolbar.actions()[len(self.toolbar.actions())-1], self.labelEdit)

        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0,0,0,0)
        vlayout.addWidget(self.toolbar)
        vlayout.addWidget(self.canvas)

        self.setLayout(vlayout)

        # Connect inputs with on_change method
        self.btnExport.clicked.connect(self._exportCSV)
        
        self.labelEdit.x_input.textChanged.connect(self._update_label)
        self.labelEdit.y_input.textChanged.connect(self._update_label)

        self.canvas.mpl_connect('button_press_event', self._onclick)      # Agrega puntos al hacer click



    # # Sobrescribiendo el metodo para que siempre este en tight layout
    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
    #     # self.canvas.figure.tight_layout()


    # Para dibujar directamente
    def draw(self):
        self.axes.relim(visible_only=True)  # autoscale solo a los objetos visibles (OBS: No considera las Collections)
        self.axes.autoscale()
        self.canvas.draw()
        # self.canvas.figure.tight_layout()

    # Borra los ejes
    def clear(self):
        self.labelEdit.x_input.setText('')
        self.labelEdit.y_input.setText('')
        self.axes.clear()
        self.canvas.draw()
        # self.canvas.figure.tight_layout()

    # def drawModule(self, H, *args, freq='rad', **kargs):
    #     try:

    #         eje, modulo, fase = ss.bode(H)      # Calculo del Bode (La fase no se usa)

    #         # Frecuencia en Hertz
    #         if freq.lower() == 'hertz' or freq.lower() == 'h':
    #             eje = eje / (2*np.pi)

    #         # Pasamos a escala logaritmica 
    #         self.axes.set_xscale('log')
            
    #         # Agregamos la cuadricula
    #         self.axes.grid(True)

    #         # Graficamos
    #         self.axes.plot(eje, modulo, *args, **kargs)
    
    #         self.canvas.figure.tight_layout()
    #         self.canvas.draw()

    #     except:
    #         print('Error al graficar')

    # Actualiza los valores de los ejes
    def _update_label(self):
        x_label = self.labelEdit.x_input.text()
        y_label = self.labelEdit.y_input.text()

        try:    # Para que no tire error al ingresar algo invalido
            self.axes.set_xlabel(x_label)
            self.axes.set_ylabel(y_label)
    
            self.draw()
        except:
            # print('Entrada inválida')
            pass

    def _exportCSV(self):

        filename, _ = QFileDialog.getSaveFileName(self, 'Export CSV', '', 'CSV File (*.csv);;All Files (*)')

        if filename:

            lines =  self.axes.get_lines()  # Arreglo de todas las curvas
            
            x_label = self.axes.get_xlabel()
            if not x_label:
                x_label = 'Eje X'   # Nombre por default
                
            # writing to csv file  
            with open(filename, 'w', newline='') as csvFile:  
                # creating a csv writer object  
                writer = csv.writer(csvFile)  
                    
                for line in lines:
                    # Escribimos los nombres
                    writer.writerow([x_label, line.get_label()])  
                        
                    # writing the data rows  
                    writer.writerows(line.get_xydata())


    def _onclick(self, event):
        #print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %(event.button, event.x, event.y, event.xdata, event.ydata))
        if event.button == 2:   # Click con la ruedita del mouse
            self.axes.plot(event.xdata, event.ydata, '.', markersize=15, zorder=3)
            self.canvas.draw()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = PlotWidget()
    w.show()
    sys.exit(app.exec())