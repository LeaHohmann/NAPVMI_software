import serial
import tkinter as tk

#bnc = serial.Serial('COM5', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)

class Channel():

    def __init__(self,name,number):
        self.name = name
        self.number = number
        self.delay = 0
        
        self.guiinit()

    def guiinit(self):
        namelabel = tk.Label(root, text="Channel {}".format(self.name))
        namelabel.pack(side=tk.LEFT, padx=5, pady=5)
        delaylabel = tk.Label(root, text=self.delay)
        delaylabel.pack(side=tk.LEFT, padx=5, pady=5)
        delayfield = tk.Entry(root)
        delayfield.pack(side=tk.LEFT, padx=5, pady=5) 

root = tk.Tk()
root.geometry("300x200+30+30")

ChA = Channel("A",1)
ChB = Channel("B",2)

root.mainloop()
