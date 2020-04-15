Imaging Software Necessary Features
-----------------------------------

#Delay generator#

**Read back the values from the BNC before changing**

**Set delays on BNC box**

**Choose one value to scan, set initial and final, step size (alternative would be number of steps but then you get weird step sizes)**  
So the rest of the delays should automatically scale with this one or depend on this one (MB-laser)


#Camera#

**Read and set gain, exposure time, x and y pixels if we don't want to use the whole image**

**Set the number of images to sum**

**Check if we saturate the camera or file format at high signal**  
? Automatic check or looking at the image live? Saturate file format??

**Take a single image**

**Display the live (rolling average of last x shots? Lots more memory? Good for low signal)**  
The camera can also display the live image without taking a shot and without saving it (not committing it to memory), so we could use that? Is there an issue with that that I am not aware of?

**Display the summed image**

**Take a single summed image while scanning the MB delay to integrate over the speed distribution in the incident beam**  
Isn't this convoluted with kinetics? 

**Do a kinetic scan with a new image at each step of the delay generator scan, link delay value to frame (absolute top priority once hardware is working but not the first thing to do for the software**

**Save the images in what format?**


#Laser#

**scan range - start, finish, step size (tell the kinetic scan how many steps it will be), dwell time (tell the camera), write wavelength so that we know what is corresponding image frame**  
Dwell time - how many images to take and sum for each wavelength?

**Go to wavelength**
 
