"""Qt & Python Based Photo Booth
By: Scott McKittrick
Features:
Configurable and selectable templates
Dependencies:
PyQt5
PyYAML
Classes Contained:
QtPyPhotobooth - Main Application controller class.
"""

################################################################
# QtPyPhotobooth Class                                         #
################################################################
class QtPyPhotobooth(QObject):
    """Main application class. Initializes and controls the application """

    ##############################
    #Screen List                 #
    ##############################
    class Screens(Enum):
        SPLASH = 0
        TEMPLATE = 1
        PREVIEW = 2
        RESULT = 3
        SAVING = 4
        SAVED = 5
        
        #-----------------------------------------------------------#    
