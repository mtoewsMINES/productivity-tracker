from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, 
                             QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox
)
from PyQt6.QtCore import Qt
from Navigation.PageButton import PageButton


"""
PageSelector:

This class is how we navigate between different pages.

Args:
    mainWindow: A reference to the page which currently contains the PageSelector.
    index:      The index of the button which should be "selected" (Denotes current page).
    popups:     Will display a popup upon changing pages. This popup will ask the user if they REALLY want to change pages.
"""
class PageSelector(QWidget):
    def __init__(self, mainWindow, index):
        super().__init__()

        self.mainWindow = mainWindow
        self.index = index
            
        layout = QHBoxLayout()

        home_button = PageButton(mainWindow, "Home", 0, index)
        activities_button = PageButton(mainWindow, "Activities", 1, index)
        stats_button = PageButton(mainWindow, "Stats", 2, index)

        self.buttons = [
              home_button,
              activities_button,
              stats_button
        ]

        layout.addWidget(home_button)
        layout.addWidget(activities_button)
        layout.addWidget(stats_button)

        self.setLayout(layout)

        self.setStyleSheet("border: 2px solid white")
        
    # Changes the current page
    def set_page(self, index):
        self.buttons[index].handlePageChange()