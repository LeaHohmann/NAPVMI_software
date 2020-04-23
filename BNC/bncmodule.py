import serial
import tkinter as tk

class DelayApp(tk.Frame):

    def __init__(self,root,port,baudrate):
        tk.Frame.__init__(self,root)
        self.pack()
        
        self.port = port
        self.baudrate = baudrate
        
        self.connect = tk.Button(self, Text="Connect to delay generator"i, command=self.connectbnc)
        self.connect.pack(side=tk.TOP, ipadx=5, ipady=5, padx=5, pady=5)

        self.message = tk.Label(self, Text="")
        self.message.pack(side=tk.BOTTOM, padx=5, pady=5)

    def connectbnc(self):
        self.bnc = serial.Serial(self.port, baudrate=self.baudrate, bytesize=8, parity="N", stopbits=1, timeout=1)

        self.message.configure(Text="Connected to BNC delay generator at interface {}".format(self.port))
        self.guiinit()
        self.connect.configure(Text="Disconnect", command=quitbnc)


    def quitbnc(self):
        self.bnc.close()

        self.frameA.destroy()
        self.frameB.destroy()
        self.frameC.destroy()
        self.frameD.destroy()
        self.frameE.destroy()
        self.frameF.destroy()
        self.frameG.destroy()
        self.frameH.destroy()

        self.connect.configure(Text="Connect", command=connectbnc)

    def guiinit(self):
        self.frameA = tk.Frame(self)
        frameA.pack(side=tk.TOP)
        ChA = Channel("A",1,frameA,self.bnc)

        self.frameB = tk.Frame(self)
        frameB.pack(side = tk.TOP)
        ChB = Channel("B",2,frameB,self.bnc)

        self.frameC = tk.Frame(self)
        frameC.pack(side=tk.TOP)
        ChC = Channel("C",3,frameC,self.bnc)

        self.frameD = tk.Frame(self)
        frameD.pack(side=tk.TOP)
        ChD = Channel("D",4,frameD,self.bnc)

        self.frameE = tk.Frame(self)
        frameE.pack(side=tk.TOP)
        ChE = Channel("E",5,frameE,self.bnc)

        self.frameF = tk.Frame(self)
        frameF.pack(side=tk.TOP)
        ChF = Channel("F",6,frameF,self.bnc)

        self.frameG = tk.Frame(self)
        frameG.pack(side=tk.TOP)
        ChG = Channel("G",7,frameG,self.bnc)

        self.frameH = tk.Frame(self)
        frameH.pack(side=tk.TOP)
        ChH = Channel("H",8,frameH,seld.bnc)


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


