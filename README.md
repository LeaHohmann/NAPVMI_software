Summary
-------

Program will contain the following modules:

- Main (file to be created)  
- Camera (cameramodule.py)  
- Delay generator (bncmodule.py)  
- Laser (file to be created)  

The modules are described in more detail below


Main
----

Main module that will contain the GUI root, define important global variables (e.g. establish serial port connection to the delay generator)


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

**Functionalties to add:**

- Read and set gain, exposure time, x and y pixels if we don't want to use the whole image  
- Set the number of images to sum  
- Check if we saturate the camera or file format at high signal    
- Take a single image  
- Display the live footage  
- For low signal: Display rolling average of last x shots?    
- Display the summed image  
- Take a single summed image while scanning the MB delay to integrate over the speed distribution in the incident beam  
- Do a kinetic scan with a new image at each step of the delay generator scan, link delay value to frame (absolute top priority once hardware is working but not the first thing to do for the software  

**Issues to think about:**

- Image file format  


Laser
-----

Module that will contain the functions to interact with the laser

**Functionalities to add:**

- Scan range - start, finish, step size (tell the kinetic scan how many steps it will be), dwell time (tell the camera), write wavelength so that we know what is corresponding image frame    
- Set wavelength  

**Issues to think about:**

What is the laser software interface??
 
