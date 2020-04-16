import serial
import tkinter as tk

bnc = serial.Serial('COM5', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)

def disconnect():
    bnc.close()
    root.quit()

class Channel():

    def __init__(self,name,number,frame):
        self.name = name
        self.number = number
        self.delay = 0
        self.frame = frame
        
        self.bncinit()
        self.guiinit()

    def guiinit(self):
        self.namelabel = tk.Label(self.frame, text="Channel {}:".format(self.name))
        self.namelabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.delaylabel = tk.Label(self.frame, text=self.delay)
        self.delaylabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.delayfield = tk.Entry(self.frame)
        self.delayfield.pack(side=tk.LEFT, padx=5, pady=5)
        self.setdelay = tk.Button(self.frame, text="Set", command=self.changedelay)
        self.setdelay.pack(side=tk.LEFT,padx=5, pady=5)

    def bncinit(self):
        inputstring = ":PULS{}:DEL?\r\n".format(self.number)
        bnc.write(inputstring.encode("utf-8"))
        lastline = bnc.readline().decode("utf-8")
        self.delay = lastline[:13]

    def guiupdate(self):
        self.delaylabel.configure(text=self.delay)
    
    def changedelay(self):
        newdelay = self.delayfield.get()
        inputstring = ":PULS{}:DEL {}\r\n".format(self.number,newdelay)
        bnc.write(inputstring.encode("utf-8"))
        lastline = bnc.readline().decode("utf-8")
        inputstring = ":PULS{}:DEL?\r\n".format(self.number)
        bnc.write(inputstring.encode("utf-8"))
        lastline = bnc.readline().decode("utf-8")
        self.delay = lastline[:13]
        self.guiupdate()
        

root = tk.Tk()
root.geometry("400x300+30+30")

frameA = tk.Frame(root)
frameA.pack(side=tk.TOP)
ChA = Channel("A",1,frameA)
frameB = tk.Frame(root)
frameB.pack(side=tk.TOP)
ChB = Channel("B",2,frameB)
frameC = tk.Frame(root)
frameC.pack(side=tk.TOP)
ChC = Channel("C",3,frameC)
frameD = tk.Frame(root)
frameD.pack(side=tk.TOP)
ChD = Channel("D",4,frameD)
frameE = tk.Frame(root)
frameE.pack(side=tk.TOP)
ChE = Channel("E",5,frameE)

Quit = tk.Button(root, text="Disconnect and Quit", command=disconnect)
Quit.pack(side=tk.TOP)

root.mainloop()
