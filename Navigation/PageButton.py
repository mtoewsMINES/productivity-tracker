from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, 
                             QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox
)
from PyQt6.QtCore import Qt

"""
PageButton:

A custom button class designed to handle page swapping.

Args:
    mainWindow:         Reference to the mainWindow.
    text:               The text that will be displayed on the button
    goto_page_index:    Index of the page that will switched to when the button is clicked.
    curr_page_index:    The index of the current page the button is on.
    popup:              Will display a popup upon changing pages. This popup will ask the user if they REALLY want to change pages.
"""
class PageButton(QPushButton):
    def __init__(self, mainWindow, text, goto_page_index, curr_page_index):
        super().__init__(text)

        self.goto_page_index = goto_page_index
        self.curr_page_index = curr_page_index
        
        self.mainWindow = mainWindow

        if goto_page_index == curr_page_index:
            self.setStyleSheet("background: light blue; color: white; font-size: 15px")
        else:
            self.setStyleSheet("font-size: 15px")

        self.clicked.connect(lambda : self.handlePageChange())

    
    def handlePageChange(self):
        self.mainWindow.set_page(self.goto_page_index)

    