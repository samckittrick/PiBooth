"""Test application to verify a template works correctly

Usage: 
python3 TemplateTester.py <templateDir>

"""

from PhotoboothTemplate import TemplateReader, ImageProcessor
import sys
from PIL import Image, ImageDraw

def generateSampleImage(imageName, width, height):
    img = Image.new("RGB", (width, height), "gray")
    draw = ImageDraw.Draw(img)
    text = imageName + "\n" + str(width) + "x" + str(height)
    textSize = draw.textsize(text)
    draw.text(((width-textSize[0])/2,(height-textSize[1])/2), str(text))
    return img


print("Qt-Py Photobooth Template Tester")
print("Validate a template and make sure it works correctly")

if(len(sys.argv) < 1):
    print ("Usage: python3 TemplateTester.py <templateDir>")
    exit()

print("--------------------------------------------\n")

#Load the template
templateDir = sys.argv[1]
print("Template Dir: " + templateDir)
tr = TemplateReader(templateDir, "template.xml")
ip = ImageProcessor(tr)

#Generate sample photos
counter = 1
imageList = list()
for imageSpec in tr.photoList:
    imageList.append(generateSampleImage("Image " + str(counter), imageSpec['width'], imageSpec['height']))
    counter += 1

#create result image.
result = ip.processImages(imageList)
result.save("result.jpg")
