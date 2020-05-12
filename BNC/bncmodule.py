import serial
import tkinter as tk

class DelayApp(tk.Frame):

    def __init__(self,root,unit):
        
        self.bnc = unit

        tk.Frame.__init__(self,root)
        self.pack()

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
        self.frameA.pack(side=tk.TOP)
        ChA = Channel("A",1,self.frameA,self.bnc)

        self.frameB = tk.Frame(self)
        self.frameB.pack(side = tk.TOP)
        ChB = Channel("B",2,self.frameB,self.bnc)

        self.frameC = tk.Frame(self)
        self.frameC.pack(side=tk.TOP)
        ChC = Channel("C",3,self.frameC,self.bnc)

        self.frameD = tk.Frame(self)
        self.frameD.pack(side=tk.TOP)
        ChD = Channel("D",4,self.frameD,self.bnc)

        self.frameE = tk.Frame(self)
        self.frameE.pack(side=tk.TOP)
        ChE = Channel("E",5,self.frameE,self.bnc)

        self.frameF = tk.Frame(self)
        self.frameF.pack(side=tk.TOP)
        ChF = Channel("F",6,self.frameF,self.bnc)

        self.frameG = tk.Frame(self)
        self.frameG.pack(side=tk.TOP)
        ChG = Channel("G",7,self.frameG,self.bnc)

        self.frameH = tk.Frame(self)
        self.frameH.pack(side=tk.TOP)
        ChH = Channel("H",8,self.frameH,self.bnc)

        self.triggeringonoff = tk.Button(self, text="Run triggering", command=self.runtriggering)
        self.triggeringonoff.pack(side=tk.TOP, ipadx=5, ipady=5, pady=20)
        


    def runtriggering(self):

        inputstring = ":PULS0:STATE 1\r\n"
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        inputstring = ":PULS0:STATE?\r\n"
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        self.bncrunning = lastline[:-2]
        if self.bncrunning == "1":
            self.triggeringonoff.configure(text="Stop triggering", command=self.stoptriggering)



    def stoptriggering(self):

        inputstring = ":PULS0:STATE 0\r\n"
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        inputstring = ":PULS0:STATE?\r\n"
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        self.bncrunning = lastline[:-2]
        if self.bncrunning == "0":
            self.triggeringonoff.configure(text="Run triggering", command=self.runtriggering)
    



class Channel():

    def __init__(self, name, number, frame, unit):

        self.name = name
        self.number = number
        self.delay = "0"
        self.frame = frame
        self.bnc = unit

        self.timeunits = {"ms": 8, "us": 5, "ns": 2}
        self.steps = {1: 0, 10: 1, 100: 2}

        self.bncinit()
        self.guiinit()



    def bncinit(self):

        inputstring = ":PULS{}:DEL?\r\n".format(self.number)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        self.delay = lastline[:-2]



    def guiinit(self):

        self.namelabel = tk.Label(self.frame, text="Channel {}:".format(self.name))
        self.namelabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.delaylabel = tk.Label(self.frame, text=self.delay)
        self.delaylabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.incrementplus = tk.Button(self.frame, text="+", command=self.plus)
        self.incrementplus.pack(side=tk.LEFT, padx=5, pady=5)
        self.incrementminus = tk.Button(self.frame, text="-", command=self.minus)
        self.incrementminus.pack(side=tk.LEFT, padx=5, pady=5)
        self.stepsize = tk.IntVar(self.frame)
        self.timeunit = tk.StringVar(self.frame)
        self.stepdropdown = tk.OptionMenu(self.frame, self.stepsize, 1, 10, 100)
        self.stepdropdown.pack(side=tk.LEFT, padx=5, pady=5)
        self.unitdropdown = tk.OptionMenu(self.frame, self.timeunit, "ns", "us", "ms")
        self.unitdropdown.pack(side=tk.LEFT, padx=5, pady=5)



    def guiupdate(self):

        self.delaylabel.configure(text=self.delay)


    
    def plus(self):

        self.increment = 1
        self.changedelay()

    

    def minus(self):

        self.increment = -1
        self.changedelay()



    def changedelay(self):
        
        timefactor = self.timeunits[self.timeunit.get()]
        step = self.steps[self.stepsize.get()]
        delayindex = step + timefactor
        newdigit = int(self.delay[-delayindex]) + self.increment
        newdelay = self.delay[:-delayindex] + str(newdigit) + self.delay[-delayindex+1:]
        inputstring = ":PULS{}:DEL {}\r\n".format(self.number,newdelay)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        inputstring = ":PULS{}:DEL?\r\n".format(self.number)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        self.delay = lastline[:-2]
        self.guiupdate()




