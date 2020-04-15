import serial
import tkinter as tk


ser = serial.Serial('COM5',baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)

def updatechannels():
    ser.write(b':PULS2:DEL?\r\n')
    lastline = ser.readline().decode("utf-8")
    delayB = lastline[:13]
    ChB.configure(text="Channel B delay: {}".format(delayB))

def changedelay(channumber):
    newdelay = Bfield.get()
    inputstring = "PULS{}:DEL {}\r\n".format(channumber,newdelay)
    ser.write(inputstring.encode("utf-8"))
    lastline = ser.readline().decode("utf-8")
    updatechannels()

def quitgui():
    ser.close()
    root.quit()

root = tk.Tk()

status = tk.Button(root, text="Status", command=updatechannels)
status.pack()

ChB = tk.Label(root, text="Channel B delay: 0")
ChB.pack()
Bfield = tk.Entry(root)
Bfield.pack()
Bchange = tk.Button(root, text="Set", command=lambda:changedelay(2))
Bchange.pack()

quit = tk.Button(root, text="Quit", command=quitgui)
quit.pack()

root.mainloop()

