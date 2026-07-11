import sys
import qdarkstyle
from PyQt6.QtWidgets import QApplication
from Navigation.MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


main()