import sys
import qdarkstyle
from PyQt6.QtWidgets import QApplication
from Navigation.MainWindow import MainWindow
from utils import load_data


def main():
    load_data()
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


main()