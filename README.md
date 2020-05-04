Summary
-------

Program will contain the following modules:

- Main (file to be created)  
- Camera (cameramodule.py)  
- Delay generator (bncmodule.py)
- Kinetic series module (file to be created)
- Delay integration scan (file to be created) 
- Laser (file to be created) 
 

The modules are described in more detail below


Main
----

Main module that will contain the GUI root, define important global variables (e.g. establish serial port connection to the delay generator, establish PySpin system instance and connection to the camera, pass the connections to the other modules as class variables)


Delay generator
---------------

Module that contains the Channels classes and other classes to interact with the delay generator (connection needs to be established in mains)

**Current functionalities:**

- Reading out and displaying the delay values from the BNC    
- Set delays on BNC box  
Delay changing might be disabled for the fixed channels (all but Molecular Beam 1) in the future  

**Functionalities to add:**

- Choose one value to scan (MB1 delay), set initial and final, step size (alternative would be number of steps but then you get weird step sizes)    

**Issues to think about:**

- Make sure USB connection is stable!!  


Camera
------

Camera module that will contain the functions to operate the camera, using the PySpin python wrapper from FLIR  

**Current functionalities:**

- Scanning for a connected cameras, if "our" camera is among it, connecting to it 
- Display the live footage 
- Check if we saturate the camera at high signal by displaying the histogram/pixel value distribution
- Read and set gain, exposure time

**Functionalties to add:**

- Set the camera to trigger mode instead of  automatic and execute the acquisition and display functions in triggered mode
- Set x and y pixels if we don't want to use the whole image  
- Set the number of images to sum  
- Take a single image/frame  
- For low signal: Display rolling average of last x shots?    
- Display the summed image 
- Save and load parameters

**Issues to think about:**

- Image file format  



Kinetic series
--------------

In setup GUI, there are separate modules for the BNC and the camera where delays/camera settings can be changed. It should also be possible to acquire single images/summed images and display the live (while the camera is being triggered) in the camera module itself. However, during a kinetic series, the program needs to access both at the same time (to give the current delay value) and cycle the delay values continuously, which can hang the GUI since it is a long-term ongoing process. Therefore the delay series should be a separate module that cycles the delay and can pass the value to both the camera (for image labeling/ file names) and the delay generator (to change the image). The setup GUI should be locked during the execution of this module so that nothing can be changed. The module needs access to the delay generator COM port connection and the system instance and camera pointer in PySpin (connections cannot be interrupted!!). Therefore the connections need to be made in the main GUI and then passed to the respective modules instead of creating them within the modules. It might be necessary to use threading to not hang the GUI while executing the kinetic series module (not sure though).

**Functionalities to add:**

- Do a kinetic scan with a new image at each step of the delay generator scan, link delay value to frame (absolute top priority once hardware is working but not the first thing to do for the software  



Delay intergration scan
-----------------------

As above, except for taking one single summed image over all the scanned delays (only 1 image file results)

**Functionalities to add:**

- Take a single summed image while scanning the MB delay to integrate over the speed distribution in the incident beam  



Laser
-----

Module that will contain the functions to interact with the laser

**Functionalities to add:**

- Scan range - start, finish, step size (tell the kinetic scan how many steps it will be), dwell time (tell the camera), write wavelength so that we know what is corresponding image frame    
- Set wavelength  

**Issues to think about:**

What is the laser software interface??
 
