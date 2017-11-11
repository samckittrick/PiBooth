"""Module that provides PyQt5 Virtual Keyboard.

By: Scott McKittrick

Classes Contained:

"""
import os
import PyQt5
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QGridLayout, QSizePolicy, QLineEdit
from PyQt5.QtCore import pyqtSignal, QSize, Qt, QEvent
from PyQt5.QtGui import QKeyEvent, QGuiApplication
from abc import ABC, ABCMeta, abstractmethod

#######################################################################################
# BasicAmericanKeyboard                                                               #
#######################################################################################
class BasicAmericanKeyboard(QWidget):
    """ Shows a basic qwerty keyboard"""

    sigShiftStateChanged = pyqtSignal()
    
    #Special Key Codes
    Key_DotCom = 1
    
    #---------------------------------------------------------------------------------#
    def __init__(self):
        super(BasicAmericanKeyboard, self).__init__()
        
        #print("Making Keyboard")
        self.capState = False
        self.shiftState = False
        self.keyboardName = "BasicAmericaKeyboard"
        #self.resDir = resDir + os.path.sep + self.KeyboardName
        
        self.buildKeyMap()
        
        #begin setting up the widget
        rowHeight = 50
        colWidth  = 50
        
        self.keyLayout = QGridLayout(self)
        self.hSpace = 10
        self.vSpace = 10
        self.keyLayout.setHorizontalSpacing(self.hSpace)
        self.keyLayout.setVerticalSpacing(self.vSpace)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        
        for lineIndex, line in enumerate(self.keyList):
            keyIndex = 0
            for key in line:
                #print("adding new key: " + key[3])
                colspan = key[5]
                #Create Key Widget
                newKey = BasicKeyWidget(key[2], key[3], rowHeight, colWidth * colspan + self.hSpace * (colspan - 1))
                newKey.setFocusPolicy(Qt.NoFocus)
                
                #Connect Signals
                #if This is a special key, use the special handler
                if(key[0] > 0):
                    newKey.sigKeyButtonClicked.connect(lambda v=key[1]: self.handleSpecialKey(v))
                else:
                    newKey.sigKeyButtonClicked.connect(lambda v=key[1]: self.handleNormalKey(v))
                self.sigShiftStateChanged.connect(lambda k=newKey: k.onShiftStateChanged(self.shiftState))
                
                #Add the key to the layout
                self.keyLayout.addWidget(newKey, lineIndex, keyIndex, 1, colspan)
                keyIndex += colspan

    #------------------------------------------------------------------------------------#
    def handleNormalKey(self, keyId):
        """Handle normal keys whose key codes are recognized by QT. """
        self.postKeyToGui(keyId, self.getValByKeyId(keyId))

    #------------------------------------------------------------------------------------#
    def handleSpecialKey(self, keyId):
        """Handle special keys whose key codes are not recognized by Qt and have to be further processed in this object."""
        #ToDo: Handle Capslock state machine.
        if(keyId == Qt.Key_Shift):
            self.shiftState = not self.shiftState
            self.sigShiftStateChanged.emit()
        elif(keyId == Qt.Key_CapsLock):
            self.capState = not self.capState
            self.shiftState = self.capState
            self.sigShiftStateChanged.emit()
        elif(keyId == BasicAmericanKeyboard.Key_DotCom):
            #keycode 0 is "not a result of a known key; for example, it may be the result of a compose sequence or keyboard macro."
            self.postKeyToGui(0, '.com')
        elif(keyId == Qt.Key_Space):
            self.postKeyToGui(keyId, " ")
        elif(keyId == Qt.Key_Enter):
            self.postKeyToGui(keyId, '')

    #------------------------------------------------------------------------------------#
    def postKeyToGui(self, keyCode, keyVal):
        """Post a key to the gui so that the focused object can read it."""

        modifier = Qt.ShiftModifier if self.shiftState else Qt.NoModifier
        
        pressEvent = QKeyEvent(QKeyEvent.KeyPress, keyCode, modifier, keyVal)
        releaseEvent = QKeyEvent(QKeyEvent.KeyRelease, keyCode, modifier)
        QGuiApplication.sendEvent(QGuiApplication.focusObject(), pressEvent)
        QGuiApplication.sendEvent(QGuiApplication.focusObject(), releaseEvent)

    #------------------------------------------------------------------------------------#
    def getValByKeyId(self, keyId):
        for line in self.keyList:
            for key in line:
                if(keyId == key[1]):
                    if(self.shiftState and key[3] != ''):
                        if(not self.capState):
                            self.shiftState = False
                            self.sigShiftStateChanged.emit()
                        return key[3]
                    else:
                        return key[2]
        
        
    #------------------------------------------------------------------------------------#
    def buildKeyMap(self):
        """ Map key ids to the values that they can represent. Special keys are ones whose keycodes require special handling in this object, normal keys are passed directly to the system. """
                #Set up the list of keys and their arrangement
        #Each key is a tuple as follows ( <specialKey>, <keycode>, <keyVal>, <shiftVal>, <rowspan>, <colSpan>)
        self.keyList = [
            #Row 1
            [ (1, Qt.Key_Escape, 'esc', '', 1, 1),
              (0, Qt.Key_QuoteLeft, '`', '~', 1, 1),
              (0, Qt.Key_1, '1', '!', 1, 1),
              (0, Qt.Key_2, '2', '@', 1, 1),
              (0, Qt.Key_3, '3', '#', 1, 1),
              (0, Qt.Key_4, '4', '$', 1, 1),
              (0, Qt.Key_5, '5', '%', 1, 1),
              (0, Qt.Key_6, '6', '^', 1, 1),
              (0, Qt.Key_7, '7', '&', 1, 1),
              (0, Qt.Key_8, '8', '*', 1, 1),
              (0, Qt.Key_9, '9', '(', 1, 1),
              (0, Qt.Key_0, '0', ')', 1, 1),
              (0, Qt.Key_Minus, '-', '_', 1, 1),
              (0, Qt.Key_Equal, '=', '+', 1, 1),
              (0, Qt.Key_Backspace, '<-','', 1, 1) ],
            #Row 2
            [ (1, Qt.Key_Tab, 'tab', '', 1, 2),
              (0, Qt.Key_Q, 'q', 'Q', 1, 1),
              (0, Qt.Key_W, 'w', 'W', 1, 1),
              (0, Qt.Key_E, 'e', 'E', 1, 1),
              (0, Qt.Key_R, 'r', 'R', 1, 1),
              (0, Qt.Key_T, 't', 'T', 1, 1),
              (0, Qt.Key_Y, 'y', 'Y', 1, 1),
              (0, Qt.Key_U, 'u', 'U', 1, 1),
              (0, Qt.Key_I, 'i', 'I', 1, 1),
              (0, Qt.Key_O, 'o', 'O', 1, 1),
              (0, Qt.Key_P, 'p', 'P', 1, 1),
              (0, Qt.Key_BracketLeft, '[', '{', 1, 1),
              (0, Qt.Key_BracketRight, ']', '}', 1, 1),
              (0, Qt.Key_Backslash, '\\','|', 1, 1)],
            #Row 3
            [ (1, Qt.Key_CapsLock, 'caps', '', 1, 2),
              (0, Qt.Key_A, 'a', 'A', 1, 1),
              (0, Qt.Key_S, 's', 'S', 1, 1),
              (0, Qt.Key_D, 'd', 'D', 1, 1),
              (0, Qt.Key_F, 'f', 'F', 1, 1),
              (0, Qt.Key_G, 'g', 'G', 1, 1),
              (0, Qt.Key_H, 'h', 'H', 1, 1),
              (0, Qt.Key_J, 'j', 'J', 1, 1),
              (0, Qt.Key_K, 'k', 'K', 1, 1),
              (0, Qt.Key_L, 'l', 'L', 1, 1),
              (0, Qt.Key_Semicolon, ';', ':', 1, 1),
              (0, Qt.Key_Enter, 'enter', '', 1, 3)],
            #Row 4
            [ (1, Qt.Key_Shift, 'shift', '', 1, 2),
              (0, Qt.Key_Z, 'z', 'Z', 1, 1),
              (0, Qt.Key_X, 'x', 'X', 1, 1),
              (0, Qt.Key_C, 'c', 'C', 1, 1),
              (0, Qt.Key_V, 'v', 'V', 1, 1),
              (0, Qt.Key_B, 'b', 'B', 1, 1),
              (0, Qt.Key_N, 'n', 'N', 1, 1),
              (0, Qt.Key_M, 'm', 'M', 1, 1),
              (0, Qt.Key_Apostrophe, ',', '<', 1, 1),
              (0, Qt.Key_Period, '.', '>', 1, 1),
              (0, Qt.Key_Slash, '/', '?', 1, 1),
              (1, Qt.Key_Shift, 'shift', '', 1, 3) ],
            #Row 5
            [ (0, Qt.Key_At, '@', '', 1, 1),
              (1, BasicAmericanKeyboard.Key_DotCom, '.com', '', 1, 3),
              (1, Qt.Key_Space, 'space', '', 1, 11 ) ] ]


        
######################################################################################
# BasicKeyWidget                                                                     #
######################################################################################
class BasicKeyWidget(QPushButton):
    """ The object representing a single square button. Can have text or an image. """

    sigKeyButtonClicked = pyqtSignal()

    #----------------------------------------------------------------------------#
    def __init__(self, keyVal, shiftVal, rowHeight, colWidth):
        """ The key that is being pressed. """
        super(BasicKeyWidget, self).__init__()
        self._key = keyVal
        self._shiftKey = shiftVal
        self.setText(self._key)
        self._size = QSize(colWidth, rowHeight)
        self.setFixedSize(self._size)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.clicked.connect(self.emitKey)

        self.shiftState = False;

    #----------------------------------------------------------------------------#
    def emitKey(self):
        """Send the keyboard notification of the key press"""
        self.sigKeyButtonClicked.emit()

    #----------------------------------------------------------------------------#
    def onShiftStateChanged(self, state):
        #print("My Shift state is changing from: " + str(self.shiftState) + " to: " + str(state))
        self.shiftState = state

        #print("My Shift: " + self._shiftKey)
        if(self._shiftKey != ''):
            self.setText(self._shiftKey if self.shiftState else self._key)

        
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    #print("Starting application")
    win = QWidget()
    layout = QGridLayout(win)
    layout.addWidget(QLineEdit(), 0, 0)
    layout.addWidget(BasicAmericanKeyboard(), 1, 0)
    win.show()
    app.exec_()
