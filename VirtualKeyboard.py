"""Module that provides PyQt5 Virtual Keyboard.

By: Scott McKittrick

Classes Contained:

"""
import os
import PyQt5
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QGridLayout, QSizePolicy
from PyQt5.QtCore import pyqtSignal, QSize
from abc import ABC, ABCMeta, abstractmethod

#######################################################################################
# BasicAmericanKeyboard                                                               #
#######################################################################################
class BasicAmericanKeyboard(QWidget):
    """ Shows a basic qwerty keyboard"""
    
    #---------------------------------------------------------------------------------#
    def __init__(self):
        super(BasicAmericanKeyboard, self).__init__()

        print("Making Keyboard")
        self.capState = False
        self.keyboardName = "BasicAmericaKeyboard"
        #self.resDir = resDir + os.path.sep + self.KeyboardName

        #Set up the list of keys and their arrangement
        #Each key is a tuple as follows ( <keyVal>, <shiftVal>, <rowspan>)
        self.keyList = [
            #Row 1
            [ ('esc', '', 1),
              ('`', '~', 1),
              ('1', '!', 1),
              ('2', '@', 1),
              ('3', '#', 1),
              ('4', '$', 1),
              ('5', '%', 1),
              ('6', '^', 1),
              ('7', '&', 1),
              ('8', '*', 1),
              ('9', '(', 1),
              ('0', ')', 1),
              ('-', '_', 1),
              ('=', '+', 1),
              ('backspace','', 1) ],
            #Row 2
            [ ( 'tab', '', 2),
              ('q', 'Q', 1),
              ('w', 'W', 1),
              ('e', 'e', 1),
              ('r', 'R', 1),
              ('t', 'T', 1),
              ('y', 'Y', 1),
              ('u', 'U', 1),
              ('i', 'I', 1),
              ('o', 'O', 1),
              ('p', 'P', 1),
              ('[', '{', 1),
              (']', '}', 1),
              ('\\','|', 1)],
            #Row 3
            [ ('caps', '', 2),
              ('a', 'A', 1),
              ('s', 'S', 1),
              ('d', 'D', 1),
              ('f', 'F', 1),
              ('g', 'G', 1),
              ('h', 'H', 1),
              ('j', 'J', 1),
              ('k', 'K', 1),
              ('l', 'L', 1),
              (';', ':', 1),
              ('enter', '', 1)],
            #Row 4
            [ ('shift', '', 2),
              ('z', 'Z', 1),
              ('x', 'X', 1),
              ('c', 'C', 1),
              ('v', 'V', 1),
              ('b', 'B', 1),
              ('n', 'N', 1),
              ('m', 'M', 1),
              (',', '<', 1),
              ('.', '>', 1),
              ('/', '?', 1),
              ('shift', '', 3) ],
            #Row 5
            [ ('@', '', 1),
              ('.com', '', 3),
              ('space', '', 11 ) ] ]

        #begin setting up the widget
        self.keyLayout = QGridLayout(self)
        
        for lineIndex, line in enumerate(self.keyList):
            for keyIndex, key, in enumerate(line):
                print("adding new key: " + key[0])
                newKey = BasicKeyWidget(key[0], key[1])
                colspan = key[2]
                #ToDo Correct colspan issue and fixed size issue
                self.keyLayout.addWidget(newKey, lineIndex, keyIndex, 1, colspan)
                
              
######################################################################################
# BasicKeyWidget                                                                     #
######################################################################################
class BasicKeyWidget(QPushButton):
    """ The object representing a single square button. Can have text or an image. """

    sigKeyButtonClicked = pyqtSignal()

    #----------------------------------------------------------------------------#
    def __init__(self, keyVal, shiftVal):
        """ The key that is being pressed. """
        super(BasicKeyWidget, self).__init__()
        self._key = keyVal
        self._shiftKey = shiftVal
        self.setText(self._key)
        self._size = QSize(50, 50)
        self.setFixedSize(self._size)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

    #----------------------------------------------------------------------------#
    def emitKey(self):
        self.sigKeyButtonClicked.emit()

        
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    print("Starting application")
    win = BasicAmericanKeyboard()
    win.show()
    app.exec_()
