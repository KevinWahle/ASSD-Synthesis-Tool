
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLineEdit, QWidget
import sys

class LabelEditWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets
        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.x_input.setPlaceholderText("Eje X")
        self.y_input.setPlaceholderText("Eje Y")

        #  Create layout
        input_layout = QHBoxLayout()

        input_layout.addWidget(self.x_input)
        input_layout.addWidget(self.y_input)

        # Assign Layout
        self.setLayout(input_layout)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = LabelEditWidget()
    w.show()
    sys.exit(app.exec())