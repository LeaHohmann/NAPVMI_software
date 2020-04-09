import numpy as np
import cv2
import matplotlib.pyplot as plt
cap = cv2.VideoCapture(0)

#rate = cv2.VideoCapture.get(CV_CAP_PROP_FPS)

print(cap.get(3),cap.get(4),cap.get(5))
print(cap.get(15))

ret = cap.set(15,-4) #-6 was the default value
ret2 = cap.set(3,480.)

print(cap.get(3),cap.get(4),cap.get(5))
print(cap.get(15))
xdim = int(cap.get(3))
ydim = int(cap.get(4))

working = np.zeros((ydim,xdim,3))
nmax = 10
ret,working = cap.read()

print('array size = ', len(working[0,]), 'by', len(working))
print('shape is', working.shape)
#import pdb; pdb.set_trace()

while (True):
    #Capture frame-by-frame
    ret, frame = cap.read()
    #Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        i = 0
        #working = 0
        working = np.zeros((ydim,xdim,3))
        #print(working)
        print('started')

        while i < nmax:
            print(i)
            #Capture frame-by-frame
            ret, frame = cap.read()
            #Our operations on the frame come here
            working = working + (frame/nmax)
            cv2.imshow('working',gray)
            i += 1

        cv2.imwrite('test2.jpg',working)
        print('done')
        #break


    if cv2.waitKey(33) & 0xFF == ord('a'):
        break

#norm = np.max(working)
#print(norm)
#working = working/norm
toplot = np.zeros((ydim,xdim))

#working.reshape(3,-1)
toplot  = working.sum(axis = 2)
#When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
print(type(toplot))
print(toplot.shape)
#cv2.imshow('working',gray)
plt.imshow(toplot,origin='upper')
plt.plot(toplot[320,])

plt.show()

print("bye bye")
