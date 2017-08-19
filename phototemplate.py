"""Module for processing and managing Photo Templates

Photo templates are packages of files that describe how many photos 
should be taken by the photo booth and how those photos should be arranged.
They also support background images and foreground overlays. 

The Photo template package is made up of an XML file called "template.xml"
and any other resources referenced in the XML. Photo templates are stored in 
their own directory called "Templates" and each template is pacakged in it's 
own directory with it's name as the directory name. Ex. Template structure.
---------------------------------
|Configurable Photo template Dir|
--------------------------------
|                             |
-------------                ----------------
| Template 1|                | Template 2   |
-------------                ----------------
|        |________,           |             |_______,
--------------   --------     ----------------     ---------
template.xml |   |img 1 |     | template.xml |     | img 2 |
--------------   --------     ----------------     ---------

By: Scott McKittrick

Dependencies: 
python3-lxml - Python bindings for libxml2 and libxslt libraries

Classes Contatined:
TemplateReader - Class that parses and contains the data in a template.xml file.
TemplateManager - Class that manages a list of available templates.
TemplateError  - Exception Class representing errors reading the template file.
"""
import os
from lxml import etree

##############################################################
# TemplateManager Class                                      #
##############################################################
class TemplateManager:
    """Class that takes a directory, reads all the templates in it and maintains a list of template objects."""

    #----------------------------------------------------------------------
    def __init__(self, dirname):
        """TemplateManager constructor
        Takes a directory name and searches that directory for photo templates."""

        self.templateDir = dirname
        self.templateList = list()

        dirList = os.listdir(dirname)
        for dir in dirList:
            try:
                reader = TemplateReader(dirname + os.path.sep + dir + os.path.sep + TemplateReader.TemplateXMLFilename)
                self.templateList.append(reader)
            except TemplateError:
                print("Error reading: " + dir + ". Not Adding")

        
##############################################################
# TemplateReader Class                                      #
##############################################################
class TemplateReader:
    """ Class that parses and contains the data in a template.xml file
    
    This class takes a directory name and searches for a template.xml file. If one is found, it will validate and read the file.

    """
    TemplateXMLFilename = "template.xml"
    TemplateXSD = "PhotoTemplate.xsd"
    NS = "{http://www.scottmckittrick.com/schema/PiBooth/PhotoTemplate}"

    #----------------------------------------------------------------------
    def __init__(self, filename):
        """Template reader constructor
        
        Parses a template package and stores the resultant data for access. 
        Throws TemplateError when it has problems parsing a template package."""
        self.TemplateFilename = filename

        try:
            print("Loading Template: " + filename)
            
            #load the template xml
            self.template_xml = etree.parse(filename)

            #validate agains the XSD file
            print("Validating template file for " + filename)
            if(self.__validateFile() != True):
                raise TemplateError("Error: XML Validation failed. ")
            else:
                print("Validation succeeded!")

            #Begin parsing the xml for data
            self.__parseFile()
                
        except OSError as err:
            print("Error reading Template: " + str(err))
            raise TemplateError("Error reading template files.")
        except etree.XMLSyntaxError as err:
            print("Error reading Template: " + str(err))
            raise TemplateError("Error parsing template xml")

    #--------------------------------------------------------------------------------
    def __validateFile(self):
        """Validates the file against a specific XML Schema Definition document. """

        xml_schema_doc = etree.parse(TemplateReader.TemplateXSD)
        xmlSchema = etree.XMLSchema(xml_schema_doc)
        
        return xmlSchema.validate(self.template_xml)

    #--------------------------------------------------------------------------------
    def __parseFile(self):
        """Parses the template.xml file and stores the data in the object"""
        root = self.template_xml.getroot()
        
        self.templateName = root.find(self.NS+"name").text
        
        descriptionElem = root.find(self.NS+"description")
        if(descriptionElem is not None):
            self.description = descriptionElem.text
            
        authorElem = root.find(self.NS+"author")
        if(authorElem is not None):
            self.author = authorElem.text

        previewImageElem = root.find(self.NS+"previewImage")
        if(previewImageElem is not None):
            self.previewImageFilename = previewImageElem.get("src")

        canvas = root.find(self.NS+"canvas")
        self.__parseCanvas(canvas)

    #--------------------------------------------------------------------------------
    def __parseCanvas(self, canvas):
        """Parses the canvas object and it's contents"""
        backgroundColorAttr = canvas.get("backgroundColor")
        if(backgroundColorAttr is not None):
            self.backgroundColor = backgroundColorAttr
            
        self.height = canvas.get("height")
        self.width = canvas.get("width")

        backgroundPhotoElem = canvas.find(self.NS+"backgroundPhoto")
        if(backgroundPhotoElem is not None):
            self.backgroundPhoto = backgroundPhotoElem.get("src")

        foregroundPhotoElem = canvas.find(self.NS+"foregroundPhoto")
        if(foregroundPhotoElem is not None):
            self.foregroundPhoto = foregroundPhotoElem.get("src")

        photoList = canvas.find(self.NS+"photos")
        self.__parsePhotoList(photoList)

    #---------------------------------------------------------------------------------
    def __parsePhotoList(self, photoList):
        """Parses the photo list object and it's contents"""
        self.photoList = list()
        for photoSpec in photoList.getchildren():
            height = photoSpec.get("height")
            width = photoSpec.get("width")
            x = photoSpec.get("x")
            y = photoSpec.get("y")
            rot = photoSpec.get("rotation")
            if(rot is None):
                rot = 0
                
            photoSpecTuple = (height, width, x, y, rot)
            self.photoList.append(photoSpecTuple)
            
    
#################################################################
# TemplateError                                                 #
#################################################################
class TemplateError(Exception):
    """Thrown for errors parsing templates."""
    pass
