import tkinter as tki
import cv2
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
import sys

width, height = 800, 600
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

root = tki.Tk()
root.bind('<Escape>', lambda e: root.quit())
lmain = tki.Label(root)
lmain.pack()

def quit_(root):
    root.destroy()
def get_resx():
    tki.Label(window,text=(cap.get(3))).pack()
def get_resy():
    tki.Label(window,text=(cap.get(4))).pack()
def get_resg():
    tki.Label(window,text=(cap.get(5))).pack()
def set_x():
    cap.set(3,newx_value)
def set_y():
    cap.set(4,newy)
def set_gain(new_gain):
    cap.set(15,new_gain)
    print('new gain is ' + str(new_gain))
def show_frame():
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame)

xwidth = cap.get(3)
ywidth = cap.get(4)
gain = cap.get(15)
xdim = int(cap.get(3))
ydim = int(cap.get(4))

top_frame = tki.Frame(root).pack(side='top')
top2_frame = tki.Frame(root).pack(side='top')
top3_frame = tki.Frame(root).pack(side='top')
bottom_frame = tki.Frame(root).pack(side='bottom')

tki.Label(top_frame,text = 'x pixels').pack(side = 'left')
tki.Label(top_frame,width = 10,text=xwidth).pack(side = 'left')
newx = tki.Entry(top_frame)
newx.pack(side = 'left')
newx_value = newx.get()
button = tki.Button(top_frame,text = 'set x',command = set_x)
button.pack(side = 'left')

#
label_ypix = tki.Label(top2_frame,text = 'y pixels').pack(side = 'left')
label_ypix_val = tki.Label(top2_frame,width = 10,text=ywidth).pack(side = 'left')
newy = tki.Entry(top2_frame).pack(side = 'left')
btn2 = tki.Button(top2_frame,text = 'set y',command = set_y).pack(side = 'left')

#
label_gain = tki.Label(top3_frame,text = 'Gain').pack(side = 'left')
label_gain_val = tki.Label(top3_frame,width = 10,text=gain).pack(side = 'left')
#new_gain= tki.Entry(top3_frame).pack(side = 'left')
gain = tki.StringVar()
gain.set('0')
entry = tki.Entry(top3_frame, textvariable= gain)
entry.pack(side = 'left')
#new_gain_p = entry.get()    ##############convert to a real number

new_gain = float(gain.get())
btn3 = tki.Button(top3_frame,text = 'set gain',command = set_gain(new_gain))
btn3.pack(side = 'left')


btn1 = tki.Button(bottom_frame,text = 'start',fg = 'green').pack()
btn_quit = tki.Button(bottom_frame,text = 'quit', command = lambda:quit_(root)).pack()


nmax = 30

while (True):
    #Capture frame-by-frame
    ret, frame = cap.read()
    #Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        i = 0
        working = 0
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
        break


    if cv2.waitKey(33) & 0xFF == ord('a'):
        break

#When everything done, release the capture

#toplot = np.zeros((ydim,xdim))
toplot  = working.sum(axis = 2)
plt.imshow(toplot,origin='upper')
#plt.plot(toplot[320,])
cap.release()
cv2.destroyAllWindows()

root.mainloop()

