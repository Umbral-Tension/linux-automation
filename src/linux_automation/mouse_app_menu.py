#!/bin/python3

import os
import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QCommandLinkButton, QBoxLayout, QWidget, QDesktopWidget
from functools import partial
import jrouter

# TODO 
# 2. REMOVE WINDOW BORDER
# 3. LAUNCHING PROGRAMS FROM A SHELL WITH AN ACTIVATED VIRTUAL ENV IS HAVING SIDE EFFECTS. EX XED SAYS SOME PYTHON LIBRARIES AREN'T PRESENT. INVESTIGATE. 


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # make launcher buttons
        self.programs = [
            'Firefox', 'Obsidian', 'Rhythmbox', 'Spotify',  
        ]
        self.websites = [
            'AudiobookBay', 'Artstation', 'Deezer', 'Github', 'Lichess', 'Lemm.ee', 'Proton','RSFW', 'Reddit', 'RedditSave', 'Youtube'
        ]
        self.buttons = {}
        for name in (self.programs + self.websites): 
            self.buttons[name] = QCommandLinkButton(name)
        spacer_button = QCommandLinkButton('---------------')
        exit_button = QCommandLinkButton('Exit')
        self.buttons['Spacer'] = spacer_button
        self.buttons['Exit'] = exit_button
        # use partial from functools to connect clicked signal to a function that has that button's name baked into it. 
        for button in self.buttons.values():
                button.clicked.connect(partial(self.button_pressed, button.text())) 

        # make layout
        button_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        for name in sorted(self.websites):
            button_layout.addWidget(self.buttons[name])
        button_layout.addWidget(self.buttons['Spacer'])
        for name in sorted(self.programs):
            button_layout.addWidget(self.buttons[name])
        button_layout.addWidget(self.buttons['Exit'])
        
        self.button_container = QWidget()
        self.button_container.setLayout(button_layout)
        self.setCentralWidget(self.button_container)


        screen_geometry = QDesktopWidget().screenGeometry()
        x = int(screen_geometry.width() / 2 - self.width() / 2)
        y = int(screen_geometry.height() / 2 - self.height() )
        self.move(x, y)
        
        


    def button_pressed(self, name):
        if name.casefold() not in ['exit', 'spacer']:
            jrouter.launch(name)
        QApplication.closeAllWindows()
        

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()