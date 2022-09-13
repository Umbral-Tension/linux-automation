#!/bin/python3

import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QCommandLinkButton, QBoxLayout, QWidget
import os.path 
import window_manager
from jtools.jconsole import test

#TODO 
# 1. FIGURE OUT HOW TO HIDE/EXIT THE PROGRAM WHEN ONE OF THE BUTTONS IS PRESSED. MAYBE EMIT A SIGNAL OR INSTANTIATE BUTTONS WITH A PARENT WIDGET PARAMETER TO GAIN ACCESS TO THE WINDOW. 
# 2. REMOVE WINDOW BORDER
# 3. LAUNCHING PROGRAMS FROM A SHELL WITH AN ACTIVATED VIRTUAL ENV IS HAVING SIDE EFFECTS. EX XED SAYS SOME PYTHON LIBRARIES AREN'T PRESENT. INVESTIGATE. 
# 4. ADD EXIT LOGIC TO EXIT BUTTON


class LauncherButton(QCommandLinkButton):
    def __init__(self, name, parent_window):
        super().__init__(name)
        self.name = name
        self.parent_window = parent_window

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.parent_window.button_pressed(self.name)
        return super().mousePressEvent(e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Window properties


        # make launcher buttons
        self.programs = [
            'Firefox', 'Joplin', 'Rhythmbox', 'Spotify',
        ]
        self.websites = [
            'AudiobookBay', 'Artstation', 'Github', 'Gmail', 'Lichess', 'R', 'RNSFW', 'RSFW', 'Reddit', 'RedditSave', 'Youtube'
        ]
        self.buttons = {}
        for name in (self.programs + self.websites): 
            self.buttons[name] = LauncherButton(name, self)
        spacer_button = LauncherButton('---------------', self)
        exit_button = LauncherButton('Exit', self)
        self.buttons['spacer'] = spacer_button
        self.buttons['Exit'] = exit_button

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

    def button_pressed(self, name):
        if name.casefold() != 'exit':
            window_manager.open(name)
        QApplication.closeAllWindows()
        

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()