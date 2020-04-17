import serial
import tkinter as tk

class Channel():

    def __init__(self, name, number, frame, unit)
        self.name = name
        self.number = number
        self.delay = 0
        self.frame = frame
        self.bnc = unit 

        self.bncinit()
        self.guiinit()

    def bncinit(self):
        inputstring = ":PULS{}:DEL?\r\n".format(self.number)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        newdelay = lastline[:-3]

    def guiinit(self):
        self.namelabel = tk.Label(self.frame, text="Channel {}:".format(self.name))
        self.namelabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.delaylabel = tk.Label(self.frame, text=self.delay)
        self.delaylabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.delayfield = tk.Entry(self.frame)
        self.delayfield.pack(side=tk.LEFT,padx=5, pady=5)
        self.setdelay = tk.Button(self.frame, text="Set", command=self.changedelay)
        self.setdelay.pack(side=tk.LEFT, padx=5, pady=5)

    def guiupdate(self):
        self.delaylabel.configure(text=self.delay)

    def changedelay(self):
        newdelay = self.delayfield.get()
        inputstring = ":PULS{}:DEL {}\r\n".format(self.number,newdelay)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        inputstring = ":PULS{}:DEL?\r\n".format(self.number)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        newdelay = lastline[:-3]
        self.guiupdate()


