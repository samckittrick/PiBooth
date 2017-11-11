# Qt-Py-Photobooth
By Scott McKittrick

Qt and Python Based photobooth applicaton for the Raspberry Pi 3 and PiCamera v2.0.

**Note: This application is still under development. It may change at any time**

## Features
* Full Touchscsreen Control
* Configurable image templates
  * Create any number of templates with overlays, backgrounds, and multiple images
  * Let your users select from a set of templates for their own custom photos
* Configurable countdown styles
  * Customize the countdown process

## Roadmap
* Configurable Color schemes
  * Match the colors to your event
* Configurable EXIF data
  * Add exif data to the images

## Installation
The following information details how to install and configure Qt-Py Photobooth.

### Dependencies
**Hardware**

* Raspberry Pi 3
* Raspberry Pi Camera Module v2.0 
* Touchscreen

**Software**

* Raspbian Stretch
* Python 3
* python3-lxml
* qt5-default
* python3-pyqt5
* python3-pyqt5.qtmultimedia
* python3-pyqt5.qtwebkit
* libqt5multimedia5-plugins
* PyYaml (installed via pip3)
* Pytz (installed via pip3)

### Getting QtPyPhotobooth
Use git to download the repository or download and unzip on the raspberry pi.
`git clone https://github.com/samckittrick/Qt-Py-Photobooth.git`

### Configuration
Qt-Py Photobooth reads a yaml configuration file called *config.yaml* in its current working directory. The default configuration file contained in the repo should have sufficient comment information to explain the different configuration options. 

### Photo Templates
Qt-Py Photobooth supports configurable photo templates that allows you to provide a range of photo formats for the user to choose from. Templates are contained within their own directory in a configurable location.

```
+----------------------+
|  Template Directory  |
+----------------------+
|
|
+----------+------------+
|          | Template 1 |
|          +------------+
|           |---> template.xml
|           |---> background.jpg
|           |---> foreground.png
|           +---> previewimg.jpg
|
+----------+------------+
           | Template 2 |
           +------------+
            |---> template.xml
            |---> background.jpg
            |---> foreground.png
            +---> previewimg.jpg
```

All templates should have a template.xml file that details information about the template. The example template should have sufficient comment information to explain the different configuration options.

**Image Generation Process**

Once the images are taken by the photobooth, the following steps are followed to place them in the template an generate the result imamge.

1. Create image canvas of the configured size and color
2. Paste background image on canvas
3. Process each image:
   i. Resize image according to configuration
   ii. Rotate image according to configuration (Note: This creates a new bounding box containing the rotated image.)
   iii. Paste the rotated image at configured coordinates. (Note: The coordinates represent the location of the upper left corner of the bounding box containing the rotated image. )
4. Paste the overlay image over the image. 

### Launching QtPy Photobooth
`python3 QtPyPhotobooth.py`
