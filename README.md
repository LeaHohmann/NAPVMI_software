Summary
-------

Program will contain the following modules:

- Main (napvmi_main.py)  
- Camera (cameramodule.py)  
- Delay generator (bncmodule.py)
- Kinetic series module (kineticseries.py)
- Delay integration scan (delayintegration.py) 
- Laser (file to be created) 


Main
----

Main module containing the GUI root. Sets up the connection to the camera and the delay generator and imports the corresponding GUIs from the other modules. Kinetic series and Delay integrationa acquisition scans can be started from main module and open in separate windows


Camera
------

Camera module (containing camera GUI). Functionalities: Setting the camera parameters (gain, exposure, region of interest, etc), displaying live images and taking individual shots, starting the triggering mode, saving individual images (as .npy or .png) and parameter files, importing previously used parameter files


Delay generator
---------------

Delay generator module (containing bnc control GUI). Functionalities: Choosing a channel & setting the delay (plus reads out current delay), starting & stopping triggering


Delay integration
-----------------

Module to start up a delay integration acquisition (summing over a range of delays). Module opens in new window and disables the other GUIs. Functionalities: Choose delay range & increments and number of frames per delay, as well as filename for the experiment. Upon start, incrementally changes the delay and takes an image, sums all images into a single image and saves as .npy, saves the camera parameters and other delays in parameter file


Kinetic series
--------------

Module to start up a kinetic series acquisition (scanning a range of delays and taking one image each). Module opens in new window and disables the other GUIs. Functionalities: Choose delay range & increments, no of frames per delay and filename for the experiment. Upon start, scans through the delay range and takes one image (consisting of multiple frames if more than 1 frame per delay was set) per delay. Saves the images as numpy arrays in a compressed numpy zip file (.npz) as well as a parameter file with camera parameters and other delays

  
Laser
-----

LEF TO DO Module that will contain the functions to interact with the laser

**Functionalities to add:**

- Scan range - start, finish, step size (tell the kinetic scan how many steps it will be), dwell time (tell the camera), write wavelength so that we know what is corresponding image frame    
- Set wavelength  

**Issues to think about:**

What is the laser software interface??




Software Requirements
---------------------

Windows: Windows 10 was used for testing the code, it has not been tested on other OS but earlier Windows might work if they can support the required python versions (some of the code is possibly Windows specific and might not work on Linux or Mac)

Python: Python >=3.4 (modules were written in and tested with Python 3.7)

Python modules:\
- numpy
- tkinter
- matplotlib
- pySerial
- PySpin (Spinnaker Python wrapper, available from FLIRs website)

Camera drivers:\
[Download Spinnaker from the FLIR website](https://www.flir.com/support-center/iis/machine-vision/downloads/spinnaker-sdk-flycapture-and-firmware-download/)\
Install according to camera instructions

BNC drivers:\
[FTDI Virtual COM port drivers](https://www.ftdichip.com/Drivers/VCP.htm)



Hardware Requirements
---------------------

Camera:\
Camera can be replaced but it should be a camera that can be controlled using the Spinnaker software (several camera series by FLIR)

Delay generator:\
Needs to be able to take SCPI commands via (virtual) serial COMM port
Written for BNC model 577

Connections:\
Camera: USB3\
Delay generator: USB (with virtual serial port drivers) or COM



Setup and hardware replacement
------------------------------

Camera:\
- Install drivers (see above) and connect camera via USB3
- The code recognizes the camera by serial number (to avoid the program trying to access eventual other cameras or devices that are connected to the computer). If a new camera is used, the serial number needs to be changed in the napvmi_main module: change the self.serialnumber attribute in the `root.__init__()` function and in the "camera not found" error message string in the `root.cameraconnect()` function.

BNC:\
- Install VCP drivers (see above)\
- Connect BNC via USB\
- Check the name/number of the virtual COM port (under serial ports in the Windows device manager). If it is not COM5, the code in the napvmi_main.py module has to be edited: Change the name to the correct one in the `root.bncconnect()` function (in the arguments of `serial.Serial()`).
- Check that the baudrate specified on the delay generator is correct (115200). If a different delay generator is used and this baudrate is not available, it has to be changed in the `root.bncconnect()` function in order to match
- If the delay generator is replaces by a different model, ensure that it can understand the same SCPI commands 

File system:\
In cameramodule.py, kineticseries.py and delayintegration.py, it may be useful to change the default directory for loading or saving files
