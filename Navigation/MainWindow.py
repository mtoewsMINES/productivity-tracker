from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
from PyQt6 import QtGui
from Pages.Home import Home
from Pages.Activities import Activities
from Pages.Stats import Stats
from utils import resource_path


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(resource_path('icon.png')))

        #create pages
        self.pages = QStackedWidget()
        self.home_page = Home(self)
        self.activities_page = Activities(self)
        self.stats_page = Stats(self)

        #add pages to stack
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.activities_page)
        self.pages.addWidget(self.stats_page)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.pages)
        self.setLayout(layout)

        #title
        self.setWindowTitle("Productivity Tool")
        self.setFixedSize(500, 750)

    def set_page(self, index):
        self.pages.setCurrentIndex(index)
        self.pages.currentWidget().clearLayout()
        self.pages.currentWidget().buildLayout()