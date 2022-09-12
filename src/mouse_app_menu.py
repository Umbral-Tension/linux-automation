#!/bin/python3

import sys
import os
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QCommandLinkButton, QBoxLayout, QWidget
import json
import os.path 
import window_manager

class LauncherButton(QCommandLinkButton):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        window_manager.open(self.name)
        return super().mousePressEvent(e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.programs = [
            'Firefox', 'Joplin', 'Rhythmbox', 'Spotify',
        ]
        self.websites = [
            'AudiobookBay', 'Artstation', 'Github', 'Gmail', 'Lichess', 'R', 'RNSFW', 'RSFW', 'Reddit', 'RedditSave', 'Youtube'
        ]

        # make launcher buttons
        self.buttons = {}
        for name in (self.programs + self.websites): 
            self.buttons[name] = LauncherButton(name)
        spacer_button = LauncherButton('---------------')
        exit_button = LauncherButton('Exit')
        self.buttons['spacer'] = spacer_button
        self.buttons['Exit'] = exit_button
    #### ADD EXIT LOGIC TO EXIT BUTTON

        # make layout
        button_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        for name in sorted(self.websites):
            button_layout.addWidget(self.buttons[name])
        button_layout.addWidget(self.buttons['spacer'])
        for name in sorted(self.programs):
            button_layout.addWidget(self.buttons[name])
        button_layout.addWidget(self.buttons['Exit'])
        
        self.button_container = QWidget()
        self.button_container.setLayout(button_layout)
        
        self.setCentralWidget(self.button_container)

    def open():
        pass

#TODO 
# 1. FIGURE OUT HOW TO HIDE/EXIT THE PROGRAM WHEN ONE OF THE BUTTONS IS PRESSED. MAYBE EMIT A SIGNAL OR INSTANTIATE BUTTONS WITH A PARENT WIDGET PARAMETER TO GAIN ACCESS TO THE WINDOW. 
# 2. REMOVE WINDOW BORDER
# 3. LAUNCHING PROGRAMS FROM A SHELL WITH AN ACTIVATED VIRTUAL ENV IS HAVING SIDE EFFECTS. EX XED SAYS SOME PYTHON LIBRARIES AREN'T PRESENT. INVESTIGATE. 
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()