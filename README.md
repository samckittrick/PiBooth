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
* libcurl4-openssl-dev
* libssl-dev
* PyYaml (installed via pip3)
* Pytz (installed via pip3)
* pycurl (installed via pip3)

### Getting QtPyPhotobooth
Use git to download the repository or download and unzip on the raspberry pi.
`git clone https://github.com/samckittrick/Qt-Py-Photobooth.git`

### Configuration
QtPy Photobooth reads a yaml configuration file called *config.yaml* in its current working directory. The default configuration file contained in the repo should have sufficient comment information to explain the different configuration options. 

### Photo Templates
QtPy Photobooth supports configurable photo templates that allows you to provide a range of photo formats for the user to choose from. Templates are contained within their own directory in a configurable location.

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

## Google Photos Integration

QtPy Photobooth can be configured to upload photos to Google Photos as they are taken. The following instructions describe how to set up Google Photos to allow this application to upload photos. Please note, you should probably still configure the LocalSave delivery mechanism so that photos are saved locally as well in case the network connection goes wrong. 

**Initial Configuration - Do Once**
1. Log in to the Google Developers Console at console.google.com
2. Create a new project and fill out the requisite details.
3. On the project dashboard go to Credentials
4. Create a new OAuth Client Id Credential Set
5. In "Type" select "Other"
6. Give the credentials a descriptive name and complete
7. Download the credentials in JSON format and place in a location where QtPY Photobooth can access them.
8. Follow the example in the config.yaml to configure the Google Photos Delivery Mechanism

**Connecting QtPy Photobooth and Google Photos - Do One or more times**
1. Launch QtPy Photobooth
2. Photobooth will begin OAuth process and display an authorization code
3. Enter authorization code at google.com/device
4. Follow the prompts to authorize the photobooth
5. Photobooth will save the resultant token in the cache location.
6. This process should only need to be done once unless the token is deleted or moved. 

**Selecting an Album - Do on Every Launch**
1. Photobooth will pop up dialog showing list of albums
2. Select album
3. Press ok.

Your photobooth can now upload photos to Google Photos
