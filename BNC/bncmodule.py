import serial
import tkinter as tk

class DelayApp(tk.Frame):

    def __init__(self,root,unit):
        
        self.bnc = unit

        tk.Frame.__init__(self,root)
        self.guiinit()


    def quitapp(self):
    
        self.frameA.destroy()
        self.frameB.destroy()
        self.frameC.destroy()
        self.frameD.destroy()
        self.frameE.destroy()
        self.frameF.destroy()
        self.frameG.destroy()
        self.frameH.destroy()


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
        ChH = Channel("H",8,frameH,self.bnc)


class Channel():

    def __init__(self, name, number, frame, unit)
        self.name = name
        self.number = number
        self.delay = 0
        self.frame = frame
        self.bnc = unit

        self.timeunits = {"ms": 0.001, "us": 0.000001, "ns": 0.000000001}

        self.bncinit()
        self.guiinit()

    def bncinit(self):
        inputstring = ":PULS{}:DEL?\r\n".format(self.number)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        self.delay = lastline[:-3]

    def guiinit(self):
        self.namelabel = tk.Label(self.frame, text="Channel {}:".format(self.name))
        self.namelabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.delaylabel = tk.Label(self.frame, text=self.delay)
        self.delaylabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.incrementplus = tk.Button(self.frame, text="+", command=self.plus)
        self.incrementplus.pack(side=tk.LEFT, padx=5, pady=5)
        self.incrementminus = tk.Button(self.frame, text="-", command=self.minus)
        self.incrementminus.pack(side=tk.LEFT, padx=5, pady=5)
        self.stepsize = tk.IntVar(self)
        self.timeunit = tk.StringVar(self)
        self.stepdropdown = tk.OptionMenu(self, self.stepsize, 1, 10, 100)
        self.stepdropdown.pack(side=tk.LEFT, pady=5, pady=5)
        self.unitdropdown = tk.OptionMenu(self, self.timeunit, "ns", "us", "ms")
        self.unitdropdown.pack(side=tk.LEFT, pady=5, pady=5)


    def guiupdate(self):
        self.delaylabel.configure(text=self.delay)

    
    def plus(self):
        timefactor = self.timeunits[self.timeunit.get()]
        self.increment = self.stepsize.get() * timefactor
        self.changedelay()

    
    def minus(self):
        timefactor = self.timeunits[self.timeunit.get()]
        self.increment = self.stepsize.get() * timefactor * -1
        self.changedelay()


    def changedelay(self):
        newdelay = self.delay + self.increment
        inputstring = ":PULS{}:DEL {}\r\n".format(self.number,newdelay)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        inputstring = ":PULS{}:DEL?\r\n".format(self.number)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        self.delay = lastline[:-3]
        self.guiupdate()




