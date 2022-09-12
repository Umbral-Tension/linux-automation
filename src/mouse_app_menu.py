import sys
import os
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QCommandLinkButton, QBoxLayout, QWidget


class LauncherButton(QCommandLinkButton):
    def __init__(self, program, path):
        super().__init__(program)
        self.program = program
        self.path = path
        

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        os.system(self.path)
        return super().mousePressEvent(e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.programs = {
            'firefox': {'path': 'firefox', 'window_info': None},
            'xed': {'path': 'xed', 'window_info': None},
            'drodo': {'path': 'firefox', 'window_info': None},
            'ebeneezer': {'path': 'xed', 'window_info': None},
        }

        # make launcher buttons
        self.buttons = {}
        for name, info in self.programs.items(): 
            self.buttons[name] = LauncherButton(name, info['path'])
        
        # make layout
        button_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        for name in sorted(self.buttons.keys()):
            button_layout.addWidget(self.buttons[name])
        
        self.button_container = QWidget()
        self.button_container.setLayout(button_layout)
        
        self.setCentralWidget(self.button_container)

#TODO 
# 1. FIGURE OUT HOW TO HIDE/EXIT THE PROGRAM WHEN ONE OF THE BUTTONS IS PRESSED. MAYBE EMIT A SIGNAL OR INSTANTIATE BUTTONS WITH A PARENT WIDGET PARAMETER TO GAIN ACCESS TO THE WINDOW. 
# 2. REMOVE WINDOW BORDER
# 3. LAUNCHING PROGRAMS FROM A SHELL WITH AN ACTIVATED VIRTUAL ENV IS HAVING SIDE EFFECTS. EX XED SAYS SOME PYTHON LIBRARIES AREN'T PRESENT. INVESTIGATE. 
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()