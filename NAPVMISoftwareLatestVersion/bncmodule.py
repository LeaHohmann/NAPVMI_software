import serial
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import ast


class DelayApp(tk.Frame):

    def __init__(self,root,unit):
        
        self.bnc = unit

        tk.Frame.__init__(self,root)
        self.pack()

        self.guiinit()
        self.initialquery()

        self.bncrunning = "0"

        self.channelnumbers = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}

        
    
    def initialquery(self):

        inputstring = ":PULS0:STATE?\r\n"
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        self.bncrunning = lastline[:-2]
        if self.bncrunning == "1":
            self.triggeringonoff.configure(text="Stop triggering", background="red", command=self.stoptriggering)
            messagebox.showinfo("Note:", "Delay generator is currently triggering")



    def guiinit(self):

        self.bnclabel = tk.Label(self, text="Delay Channel Control", anchor=tk.NW, font=("Helvetica", 18))
        self.bnclabel.pack(pady=(10,30))

        self.tunerframe = tk.Frame(self)
        self.tunerframe.pack(side=tk.TOP)

        self.channelname = tk.StringVar(self.tunerframe)
        self.channeltuner = tk.OptionMenu(self.tunerframe, self.channelname, "A", "B", "C", "D", "E", "F", "G", "H")
        self.channeltuner.pack(side=tk.LEFT, pady=(10,5), padx=(0,10))

        self.channelset = tk.Button(self.tunerframe, text="Set Channel", command=self.setchannel)
        self.channelset.pack(side=tk.LEFT, pady=(10,5))

        self.channelframe = tk.Frame(self)
        self.channelframe.pack(side=tk.TOP)

        self.triggeringonoff = tk.Button(self, text="Run triggering", background="green", command=self.runtriggering)
        self.triggeringonoff.pack(side=tk.TOP, ipadx=5, ipady=5, pady=(30,10))

        self.delayfileframe = tk.Frame(self)
        self.delayfileframe.pack(side=tk.TOP, pady=(10,5))

        self.savedelays = tk.Button(self.delayfileframe, text="Save current delays to file", command=self.savedelayfile)
        self.savedelays.pack(side=tk.LEFT, padx=5)

        self.loaddelays = tk.Button(self.delayfileframe, text="Load delays from file", command=self.loaddelayfile)
        self.loaddelays.pack(side=tk.LEFT, padx=5)



    def setchannel(self):
        
        try:
            self.channel.destroy()
        except AttributeError:
            pass
        
        channelname = self.channelname.get()
        channelnumber = self.channelnumbers[channelname]

        self.channel = Channel(channelname, channelnumber, self.channelframe, self.bnc) 
        


    def runtriggering(self):

        inputstring = ":PULS0:STATE 1\r\n"
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        inputstring = ":PULS0:STATE?\r\n"
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        self.bncrunning = lastline[:-2]
        if self.bncrunning == "1":
            self.triggeringonoff.configure(text="Stop triggering", background="red", command=self.stoptriggering)



    def stoptriggering(self):

        inputstring = ":PULS0:STATE 0\r\n"
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        inputstring = ":PULS0:STATE?\r\n"
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        self.bncrunning = lastline[:-2]
        if self.bncrunning == "0":
            self.triggeringonoff.configure(text="Run triggering", background="green", command=self.runtriggering)

    

    def savedelayfile(self):
        
        delaydict = {}

        for i in self.channelnumbers:
            number = self.channelnumbers[i]
            inputstring = ":PULS{}:DEL?\r\n".format(number)
            self.bnc.write(inputstring.encode("utf-8"))
            lastline = self.bnc.readline().decode("utf-8")
            self.delay = lastline[:-2]
            delaydict[i] = self.delay

        filename = filedialog.asksaveasfilename(initialdir="C:/", title="Save delay settings:", filetypes=(("Text files", "*.txt"),("All files", "*.*")))
        f = open(filename, "w")
        f.write(str(delaydict))
        f.close()



    def loaddelayfile(self):

        filename = filedialog.askopenfilename(initialdir="C:/", title="Load delay settings from file:", filetypes=(("Text files", "*.txt"),("All files", "*.*")))
        f = open(filename, "r")
        delaydict = ast.literal_eval(f.read())

        for i in delaydict:
            newdelay = delaydict[i]
            inputstring = ":PULS{}:DEL {}\r\n".format(self.channelnumbers[i],newdelay)
            self.bnc.write(inputstring.encode("utf-8"))
            lastline = self.bnc.readline().decode("utf-8")
        
        try:
            inputstring = ":PULS{}:DEL?\r\n".format(self.channel.number)
            self.bnc.write(inputstring.encode("utf-8"))
            lastline = self.bnc.readline().decode("utf-8")
            self.channel.delay = lastline[:-2]
            self.channel.guiupdate()
        except AttributeError:
            pass
        
        messagebox.showinfo("File loaded", "All channel delays updated from file.")



    def quitapp(self):
    
        if self.bncrunning == "1":
            self.stoptriggering()




class Channel(tk.Frame):

    def __init__(self, name, number, master, unit):

        tk.Frame.__init__(self,master)
        self.pack()
        
        self.name = name
        self.number = number
        self.delay = "0"
        self.bnc = unit

        self.timeunits = {"ms": 100000000, "us": 100000, "ns": 100}

        self.bncinit()
        self.guiinit()



    def bncinit(self):

        inputstring = ":PULS{}:DEL?\r\n".format(self.number)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        self.delay = lastline[:-2]



    def guiinit(self):

        self.namelabel = tk.Label(self, text="Channel {}:".format(self.name), font=("Helvetica", 12))
        self.namelabel.pack(side=tk.TOP, padx=5, pady=(10,5))
        self.delaylabel = tk.Label(self, text=self.delay, font=("Helvetica", 12))
        self.delaylabel.pack(side=tk.TOP, padx=5, pady=5)
        self.incrementplus = tk.Button(self, text="+", command=self.plus, font=("Arial", 12))
        self.incrementplus.pack(side=tk.LEFT, padx=5, pady=5)
        self.incrementminus = tk.Button(self, text=u"\u2212", command=self.minus, font=("Arial", 12))
        self.incrementminus.pack(side=tk.LEFT, padx=5, pady=5)
        self.stepsize = tk.IntVar(self)
        self.timeunit = tk.StringVar(self)
        self.stepdropdown = tk.OptionMenu(self, self.stepsize, 1, 10, 100)
        self.stepdropdown.pack(side=tk.LEFT, padx=5, pady=5)
        self.stepdropdown.configure(height=2)
        self.unitdropdown = tk.OptionMenu(self, self.timeunit, "ns", "us", "ms")
        self.unitdropdown.pack(side=tk.LEFT, padx=5, pady=5)
        self.unitdropdown.configure(height=2)




    def guiupdate(self):

        self.delaylabel.configure(text=self.delay)


    
    def plus(self):

        self.increment = 1
        self.changedelay()

    

    def minus(self):

        self.increment = -1
        self.changedelay()



    def changedelay(self):

        inputstring = ":PULS{}:DEL?\r\n".format(self.number)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        if lastline[:-2] != self.delay:
            messagebox.showerror("Error:", "Delay was out of sync due to manual change. No incrementing performed. Delay will be updated to the current value and can be altered again after.")
            self.delay = lastline[:-2]
            self.guiupdate()
            return

        
        try:
            if self.delay[0] == "-":
                self.increment *= -1
                self.parity = -1
            else:
                self.parity = 1
            dotindex = self.delay.index(".")
          
            timefactor = self.timeunits[self.timeunit.get()]
            step = int(self.stepsize.get())
            increment = timefactor*step*self.increment
            newvalue = int(self.delay[-11:]) + increment
            
            if newvalue < 0:
                newvalue *= -1
                
                if int(self.delay[:dotindex]) != 0 and self.parity == 1:
                    newseconds = str(int(self.delay[:dotindex]) -1*self.parity)
                    newvalue = 100000000000 - newvalue
                elif int(self.delay[:dotindex]) != 0 and self.parity == -1:
                    newseconds = "-" + str(int(self.delay[:dotindex]) -1*self.parity)
                    newvalue = 100000000000 - newvalue
                elif self.parity == -1:
                    newseconds = self.delay[1:dotindex]
                else:
                    newseconds = "-" + self.delay[:dotindex]

                newdecimals = str(newvalue)

                    
            else:        

                newdecimals = str(newvalue)

                if len(newdecimals) <= 11:
                    newseconds = self.delay[:dotindex]
        
                elif len(newdecimals) > 11:
                    newseconds = str(int(self.delay[:dotindex]) + 1*self.parity)
                    newdecimals = newdecimals[:-11]

            if len(newdecimals) < 11:
                newdecimals = newdecimals.zfill(11)

            newdelay = newseconds + "." + newdecimals


            inputstring = ":PULS{}:DEL {}\r\n".format(self.number,newdelay)
            self.bnc.write(inputstring.encode("utf-8"))
            lastline = self.bnc.readline().decode("utf-8")
            inputstring = ":PULS{}:DEL?\r\n".format(self.number)
            self.bnc.write(inputstring.encode("utf-8"))
            lastline = self.bnc.readline().decode("utf-8")
            self.delay = lastline[:-2]
            self.guiupdate()

        except KeyError:
            messagebox.showerror("Error", "Please set an increment and a time unit")




