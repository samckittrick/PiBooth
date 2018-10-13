
from mainwindow import MainGuiWindow
import PyQt5
from PyQt5.QtWidgets import QApplication

####################################
#Main function
####################################
if(__name__ == '__main__'):
    import sys

    app = QApplication(sys.argv)
    screenRes = app.desktop().screenGeometry()
    width, height = screenRes.width(), screenRes.height()
    print("Width: " + str(width))
    print("Height: " + str(height))
    
    mApplication = MainGuiWindow(width, height,"res/logo.jpg")
    mApplication.initUI()
    mApplication.showMainWindow()
    
    sys.exit(app.exec_())
