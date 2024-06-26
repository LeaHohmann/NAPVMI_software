import serial
import ast
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext as scroll
import datetime
from datetime import date
import threading
import time
import subprocess
import os


class MotorApp(tk.Tk):

    def __init__(self):

        tk.Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.closegui)

        self.title("Motor control")

        self.motorstatus = {"X": 0, "Y": 0, "Z": 0, "R": 0}
        self.globalstatus = 0

        self.serialnumbers = {"X": "20052-011", "Y": "20052-012", "Z": "20052-013", "R": "20052-014"}
        
        self.upperframe = tk.Frame(self)
        self.upperframe.pack(side=tk.TOP)
        
        self.lowerframe = tk.Frame(self)
        self.lowerframe.pack(side=tk.TOP)

        self.statusframe = tk.Frame(self.upperframe, height=300, width=250)
        self.statusframe.pack(side=tk.LEFT,padx=5)
        self.statusframe.pack_propagate(0)

        self.controlframe = tk.Frame(self.upperframe, height=300, width=700)
        self.controlframe.pack(side=tk.LEFT, padx=5)
        self.controlframe.pack_propagate(0)

        self.menuframe = tk.Frame(self.upperframe, height=300, width=200)
        self.menuframe.pack(side=tk.LEFT, padx=5)
        self.menuframe.pack_propagate(0)
        
        self.overrideframe = tk.Frame(self.lowerframe,height=50)
        self.overrideframe.pack(side=tk.TOP, pady=5)
        
        self.xlimits = (-5000,5000)
        self.ylimits = (-4500,4500)
        self.zlimits = (400,80000)
        self.rlimits = (-3600,3600)
        
        self.xmmlimits = ("-25mm","25mm")
        self.ymmlimits = ("-22.5mm","22.5mm")
        self.zmmlimits = ("0mm","400mm")
        self.rdeglimits = ("-360 degrees","360 degrees")
        
        self.errorcodes = {"-1": "Stop motor first", "-2": "Invalid argument", "-3": "Cannot query this option", "-5": "Action failed due to internal error", "-6": "Command unavailable in current mode", "-7": "Motor is disabled", "-101": "Wrong argument type", "-102": "Invalid number of arguments"}

        self.today = date.today()
        
        self.portnum = 2
        
        self.connectbutton = tk.Button(self.controlframe, text="Connect to motors", command=self.portconnect)
        self.connectbutton.pack(side=tk.TOP)
        
        self.units = {"X": "mm", "Y": "mm", "Z": "mm", "R": u"\N{DEGREE SIGN}"}
        
        self.positioncall = False
        


    
    def portconnect(self):
    
        if self.portnum == 5:
        
            self.portnum += 1
            self.portconnect()
            return
            
        if self.portnum == 4:
        
            self.portnum += 2
            self.portconnect()
            return
            
        else:
        
            try:
                string = "COM{}".format(self.portnum)
                self.port = serial.Serial(string,baudrate=115200,bytesize=8,parity="N",stopbits=1,timeout=30)
            
                self.port.write("SER\r\n".encode("utf-8"))
                lastline = self.port.readline().decode("utf-8")
                
                if self.serialnumbers["X"] in lastline:

                    self.port.close()
                    self.xport = serial.Serial(string,baudrate=115200,bytesize=8,parity="N",stopbits=1,timeout=30)
                    self.motorstatus["X"] = 1
                    self.globalstatus += 1

                elif self.serialnumbers["Y"] in lastline:

                    self.port.close()
                    self.yport = serial.Serial(string,baudrate=115200,bytesize=8,parity="N",stopbits=1,timeout=30)
                    self.motorstatus["Y"] = 1
                    self.globalstatus += 1

                elif self.serialnumbers["Z"] in lastline:

                    self.port.close()
                    self.zport = serial.Serial(string,baudrate=115200,bytesize=8,parity="N",stopbits=1,timeout=30)
                    self.motorstatus["Z"] = 1
                    self.globalstatus += 1

                elif self.serialnumbers["R"] in lastline:

                    self.port.close()
                    self.rport = serial.Serial(string,baudrate=115200,bytesize=8,parity="N",stopbits=1,timeout=30)
                    self.motorstatus["R"] = 1
                    self.globalstatus += 1
                    
            except:
                
                if self.portnum < 10:
                
                    self.portnum += 1
                    self.portconnect()
                    return

            if self.globalstatus == 4:
            
                self.loadcurrent()
                
           
            elif self.portnum < 10:

                self.portnum += 1
                self.portconnect()
                return

            else:

                self.port.close()
                
                string = ""

                for motor, stat in self.motorstatus.items():
                    if stat == 0:
                        string += "{} ".format(motor)

                answer = messagebox.askretrycancel("Error:", "Motors {} could not be found. Retry connection?".format(string))

                if answer:
                    self.portnum = 2
                    self.portconnect()

                else:
                    self.closegui()
                    
    
    
    def steptomm(self,stepvalue):
    
        microns = stepvalue*5
        mm = str(microns/1000)
    
        return(mm)
        
        
        
    def mmtostep(self,mminput):
    
        if "." in mminput:
        
            mm = mminput[0:mminput.index(".")]
            um = mminput[mminput.index(".")+1:]
            
            umtotal = int(mm)*1000 + int(um)
        
            if umtotal%5 < 3:
                step = umtotal//5
            else:
                step = umtotal//5 + 1
            
        elif "," in mminput:
        
            mm == mminput[0:mminput.index(",")]
            um == mminput[mminput.index(",")+1:]
            
            umtotal = int(mm)*1000 + int(um)
            
            if umtotal%5 < 3:
                step = umtotal//5
            else:
                step = umtotal//5 +1
            
        else:
        
            um = int(mminput)*1000
            step = int(um//5)
        
        return(step)
        
        
    
    def steptodegree(self,stepvalue):
    
        degree = str(stepvalue/10)
        
        return(degree)
        
    
    
    def degreetostep(self,degreestring):
    
        deg = float(degreestring)
        step = int(round(deg*10))
        
        return(step)

    
    
    def loadcurrent(self):
    
        self.xport.write("PACT\r\n".encode("utf-8"))
        response = self.xport.readline().decode("utf-(").split(",")
        xselfloc = response[2][0:-5]
        self.yport.write("PACT\r\n".encode("utf-8"))
        response = self.yport.readline().decode("utf-(").split(",")
        yselfloc = response[2][0:-5]
        self.zport.write("PACT\r\n".encode("utf-8"))
        response = self.zport.readline().decode("utf-(").split(",")
        zselfloc = response[2][0:-5]
        self.rport.write("PACT\r\n".encode("utf-8"))
        response = self.rport.readline().decode("utf-(").split(",")
        rselfloc = response[2][0:-5]
        
        f = open("current.txt", "r")
        current = ast.literal_eval(f.read())
        f.close()
        
        if xselfloc != current["X"] or yselfloc != current["Y"] or zselfloc != current["Z"] or rselfloc != current["R"]:
            result = messagebox.askyesnocancel("Out of sync","The position information stored on motors does not match the current position file. Last position on file (saved on {}) is: X: {}, Y: {}, Z: {}, R: {}. Last position on motors is: X: {}, Y: {}, Z: {}, R: {}. Override options: \n YES: Use motor position (override file). \n NO: Use file position (override motor saved position). \n CANCEL: Close program and open position file for edit.".format(current["date"],current["X"],current["Y"],current["Z"],current["R"],xselfloc,yselfloc,zselfloc,rselfloc))
        
            if result:
                
                xpos = xselfloc
                ypos = yselfloc
                zpos = zselfloc
                rpos = rselfloc
                          
                f = open("current.txt", "w")
                current = {"date": self.today.strftime("%y%m%d"), "X": xselfloc, "Y": yselfloc, "Z": zselfloc, "R": rselfloc}
                f.write(str(current))
                f.close()
                
                self.initiatemotors(xpos,ypos,zpos,rpos)

                
            elif result is None:
            
                subprocess.call(["cmd.exe", "/c", "current.txt"])
                self.closegui()
                
            else:
            
                xpos = current["X"]
                ypos = current["Y"]
                zpos = current["Z"]
                rpos = current["R"]
                
                inputstring = "PACT,{}\r\n".format(xpos)
                self.xport.write(inputstring.encode("utf-8"))
                lastline = self.xport.readline()
                inputstring = "PACT,{}\r\n".format(ypos)
                self.yport.write(inputstring.encode("utf-8"))
                lastline = self.yport.readline()
                inputstring = "PACT,{}\r\n".format(zpos)
                self.zport.write(inputstring.encode("utf-8"))
                lastline = self.zport.readline()
                inputstring = "PACT,{}\r\n".format(rpos)
                self.rport.write(inputstring.encode("utf-8"))
                lastline = self.rport.readline()
                
                self.initiatemotors(xpos,ypos,zpos,rpos)
        
                       

        else:
            result = messagebox.askquestion("Confirm position", "The last used position (saved on {}) is: X: {}, Y: {}, Z: {}, R: {}. Would you like to set this as current position (only click yes, if position has not been changed since then)? If no, the program will be closed and the position storage file will be opened for edit. Edit the position and run program again.".format(current["date"],current["X"],current["Y"],current["Z"],current["R"]))
        
            if result == "yes":
        
                xpos = current["X"]
                ypos = current["Y"]
                zpos = current["Z"]
                rpos = current["R"]
                
                self.initiatemotors(xpos,ypos,zpos,rpos)
            
            
            else:
        
                subprocess.call(["cmd.exe", "/c", "current.txt"])
                self.closegui()
                return
                
        

    def initiatemotors(self,xpos,ypos,zpos,rpos):
    
        xmmpos = self.steptomm(int(xpos))
        ymmpos = self.steptomm(int(ypos))
        zmmpos = self.steptomm(int(zpos))
        rdegpos = self.steptodegree(int(rpos))

        self.x = Motor(self,"X",self.xport,xpos,xmmpos,self.xlimits,self.xmmlimits)
        self.y = Motor(self,"Y",self.yport,ypos,ymmpos,self.ylimits,self.ymmlimits)
        self.z = Motor(self,"Z",self.zport,zpos,zmmpos,self.zlimits,self.zmmlimits)
        self.r = Motor(self,"R",self.rport,rpos,rdegpos,self.rlimits,self.rdeglimits)
        
    
        self.running = True
        self.connected = True
        
        self.secondthread()
        self.thirdthread()
        self.fourththread()
        self.fifththread()
        
        self.globalstatus = 5
        self.connectbutton.destroy()
        self.guiinit()
        
        
    
    def guiinit(self):


        #Status frame
        
        self.statusheader = tk.Label(self.statusframe, text="Error Log", font=("Helvetica",14))
        self.statusheader.pack(side=tk.TOP, pady=(5,10))
        
        self.errorlog = scroll.ScrolledText(self.statusframe, width = 35, height = 20, font=("Courier",12))
        self.errorlog.pack(side=tk.TOP)
        self.errorlog.insert(tk.END, "{}\n".format(self.today.strftime("%y%m%d")))
        
        
        #Control frame
        
        self.controlheader = tk.Label(self.controlframe, text="Motor control", font=("Helvetica",14))
        self.controlheader.pack(side=tk.TOP, pady=(5,50))
        
        self.x.guipack()
        self.y.guipack()
        self.z.guipack()
        self.r.guipack()
        
        self.stopbutton = tk.Button(self.controlframe, text="Emergency stop", background="red", command=self.emergencystop)
        self.stopbutton.pack(side=tk.TOP,pady=10)


        #Menu frame
        
        self.menuheader = tk.Label(self.menuframe, text="Saved positions", font=("Helvetica",14))
        self.menuheader.pack(side=tk.TOP, pady=(5,50))
        
        self.nofavlabel = tk.Label(self.menuframe, text="There are no saved positions availale")
        
        self.favframe = tk.Frame(self.menuframe)
        self.favframe.pack(side=tk.TOP,pady=(5,10))
        
        self.favourites = tk.Listbox(self.favframe, selectmode=tk.SINGLE)
        
        self.menubuttonframe = tk.Frame(self.menuframe)
        self.menubuttonframe.pack(side=tk.TOP)
        
        self.savebutton = tk.Button(self.menubuttonframe, text="Save current", command=self.savefavourite)
        self.savebutton.pack(side=tk.LEFT)
        
        self.setbutton = tk.Button(self.menubuttonframe, text="Set position", command=self.setfavourite)
        
        self.loadfavourites()
        
        
        #Override frame
        
        self.overridevar = tk.IntVar()
        self.overridebutton = tk.Checkbutton(self.overrideframe, text="Override motor limits for single move", variable=self.overridevar)
        self.overridebutton.pack(side=tk.TOP)
        
        self.reloverridevar = tk.IntVar()
        self.reloverridebutton = tk.Checkbutton(self.overrideframe, text="Override relative limits for single move", variable=self.reloverridevar)
        self.reloverridebutton.pack(side=tk.TOP)
        
        
    def loadfavourites(self):
    
        if os.path.getsize("favs.txt") == 0:
        
            self.nofavlabel.pack(side=tk.TOP,pady=5)
            self.favs = {}
            self.nofavs = True
            
        else:
            
            f = open("favs.txt", "r")
            self.favs = ast.literal_eval(f.read())
            f.close()
            
            self.favourites.pack(side=tk.TOP)
        
            for i in self.favs.keys():
                
                self.favourites.insert(tk.END, i)
            
            self.setbutton.pack(side=tk.LEFT)
            
            self.nofavs = False
        
        
        
    def secondthread(self):
        
        t2 = threading.Thread(target=self.x.update)
        t2.daemon = True
        t2.start()
        
        
        
    def thirdthread(self):
    
        t3 = threading.Thread(target=self.y.update)
        t3.daemon = True
        t3.start()
        
        
        
    def fourththread(self):
    
        t4 = threading.Thread(target=self.z.update)
        t4.daemon = True
        t4.start()
        
        
        
    def fifththread(self):
    
        t5 = threading.Thread(target=self.r.update)
        t5.daemon = True
        t5.start()
        
           

    def emergencystop(self):

        self.running = False
        
        self.x.emergencystop()
        self.y.emergencystop()
        self.z.emergencystop()
        self.r.emergencystop()
        
        self.running = True
        
        self.stopbutton.configure(text="Restart", command=self.restart)
        messagebox.showinfo("Emergency stop", "Emergency stop was executed. Motor is now disabled; when the problem is fixed, clear errors to return motor to operational state and then click restart")
        
        currenttime = time.strftime("%H:%M:%S", time.localtime())
        errormsg = "{} EMERGENCY STOP".format(currenttime)
        self.errorlog.insert(tk.END, errormsg)
        
        

    def restart(self):
    
        self.stopbutton.configure(text="Emergency Stop", command=self.emergencystop)
        
        self.x.startbutton.configure(state=tk.NORMAL)
        self.x.stopbutton.configure(state=tk.NORMAL)
        self.y.startbutton.configure(state=tk.NORMAL)
        self.y.stopbutton.configure(state=tk.NORMAL)
        self.z.startbutton.configure(state=tk.NORMAL)
        self.z.stopbutton.configure(state=tk.NORMAL)
        self.r.startbutton.configure(state=tk.NORMAL)
        self.r.stopbutton.configure(state=tk.NORMAL)
      



    def setfavourite(self):
        
        choice = str(self.favourites.get(self.favourites.curselection()))
        setposition = self.favs[choice]
        
        self.positioncall = True
        
        self.z.moveto(int(setposition["Z"]))
        self.x.moveto(int(setposition["X"]))
        self.y.moveto(int(setposition["Y"]))
        self.r.moveto(int(setposition["R"]))
        
        self.positioncall = False
        
        
    
    def savefavourite(self):
    
        xmoving = self.x.querymovement()
        ymoving = self.y.querymovement()
        zmoving = self.z.querymovement()
        rmoving = self.r.querymovement()
        
        if xmoving or ymoving or zmoving or rmoving:
        
            messagebox.showerror("Error", "Cannot save position while motors are moving")
            
        else:
        
            self.popup = tk.Toplevel(self)
            self.popup.title("Save current position")
            self.popupheader = tk.Label(self.popup, text="Choose name to save position under (do not choose existing name unless you want to overwrite it!)", font=("Helvetica",12))
            self.popupheader.pack(side=tk.TOP)
            self.nameentry = tk.Entry(self.popup)
            self.nameentry.pack(side=tk.TOP, pady=10)
            self.namebutton = tk.Button(self.popup, text="Save", command=self.saveundername)
            self.namebutton.pack(side=tk.TOP)
        
        
    
    def saveundername(self):
    
        newname = str(self.nameentry.get())
        self.favs[newname] = {"X": self.x.pos, "Y": self.y.pos, "Z": self.z.pos, "R": self.r.pos}
        
        f = open("favs.txt", "w")
        f.write(str(self.favs))
        f.close()
        
        self.favourites.insert(tk.END, newname)
        
        self.popup.destroy()
        
        if self.nofavs:
            
            self.nofavlabel.pack_forget()
            self.favourites.pack()
            self.setbutton.pack()
        
        
   
    def closegui(self):
        
        if self.globalstatus == 5:
        
            xmoving = self.x.querymovement()
            ymoving = self.y.querymovement()
            zmoving = self.z.querymovement()
            rmoving = self.r.querymovement()
            
            if xmoving or ymoving or zmoving or rmoving:
            
                messagebox.showerror("Error", "Please wait for motors to stop moving before closing program")
                return
            
            f = open("current.txt", "w")
            current = {"date": self.today.strftime("%y%m%d"), "X": self.x.pos, "Y": self.y.pos, "Z": self.z.pos, "R": self.r.pos}
            f.write(str(current))
            f.close()
                    
            logtext = "\n\n" +  self.errorlog.get("1.0", tk.END)
            f = open("errorlog.txt", "a")
            f.write(logtext)
            f.close()
                
                    
            self.running = False
            self.connected = False
            
            self.xport.close()
            self.yport.close()
            self.zport.close()
            self.rport.close()
            
            self.destroy()
            
            
        elif self.globalstatus == 4:
        
            self.xport.close()
            self.yport.close()
            self.zport.close()
            self.rport.close()
            
            self.destroy()
        
            
        else:
        
            self.destroy()
        
 
 

class Motor():

    def __init__(self,master,name,unit,position,unitposition,limits,unitlimits):
    
        
        self.name = name
        self.motor = unit
        self.limits = limits
        self.master = master
        self.pos = position
        self.unitpos = unitposition
        self.unitlimits = unitlimits
        
        self.units = self.master.units[self.name]
        
        self.guiinit()
        
        
    
    def guiinit(self):
    
        self.frame = tk.Frame(self.master.controlframe)
        self.Label = tk.Label(self.frame, text="Motor {}".format(self.name), font=("Helvetica",12))
        self.Label.pack(side=tk.LEFT, padx=(0,5))
        self.poslabel = tk.Label(self.frame, text=self.pos, font=("Helvetica",12), width=10)
        self.poslabel.pack(side=tk.LEFT, padx=5)
        self.entry = tk.Entry(self.frame)
        self.entry.pack(side=tk.LEFT, padx=5)
        self.unitposlabel = tk.Label(self.frame, text=self.unitpos+" "+self.units, font=("Helvetica",12), width=10)
        self.unitposlabel.pack(side=tk.LEFT, padx=5)
        self.unitentry = tk.Entry(self.frame)
        self.unitentry.pack(side=tk.LEFT, padx=5)
        self.startbutton = tk.Button(self.frame, text="Start", command=self.changeposition)
        self.startbutton.pack(side=tk.LEFT, padx=5)
        self.stopbutton = tk.Button(self.frame, text="Stop", command=self.stopmotor)
        self.stopbutton.pack(side=tk.LEFT, padx=5)
        self.clearbutton = tk.Button(self.frame, text="Clear error", command=self.clearerror)
        self.clearbutton.pack(side=tk.LEFT,padx=5)
          
        
        
    def guipack(self):
    
        self.frame.pack(side=tk.TOP, pady=5)
        
        
        
    def update(self):
    
        while self.master.connected == True:
        
            time.sleep(0.5)
        
            if self.master.running:
        
                self.motor.write("PACT\r\n".encode("utf-8"))
                try:
                    response = self.motor.readline().decode("utf-8").split(",")
                    self.pos = response[2][0:-5]
                except RecursionError:
                    self.pos = "Error"
            
                self.poslabel.configure(text=self.pos)
                
                if self.pos != "Error":
                    if self.name == "R":
                        self.unitpos = str(self.master.steptodegree(int(self.pos)))
                        self.unitposlabel.configure(text=self.unitpos+" "+self.units)
                    else:
                        self.unitpos = str(self.master.steptomm(int(self.pos)))
                        self.unitposlabel.configure(text=self.unitpos+" "+self.units)
        
        
        
    def changeposition(self):

        try:
            self.newpos = int(self.entry.get())
            
        except ValueError:
            
            try:
                unitnewpos = str(self.unitentry.get())
                if self.name == "R":
                    self.newpos = self.master.degreetostep(unitnewpos)
                else:
                    self.newpos = self.master.mmtostep(unitnewpos)
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a position to set")
                return

        self.moveto(self.newpos)
            
            
            
    def moveto(self,newposition):
    
        if self.master.overridevar.get() and self.master.reloverridevar.get() == 1:
        
            answer = messagebox.askquestion("Caution: Limit override", "Override of absolute and relative motor limits is selected. Are you sure you want to proceed without checking limits? Only click YES if you are sure that the position can be reached without damaging motors.")
            
            if answer == "yes":
            
                self.runmotor(newposition)
                
            self.master.overridebutton.deselect()
            self.master.reloverridebutton.deselect()
                
                
        elif self.master.overridevar.get():
        
            answer = messagebox.askquestion("Caution: Absolute limit override", "Override of absolute motor limits is selected. Are you sure you want to proceed without checking limits? Only click YES if you are sure that the position can be reached without damaging motors.")
                 
            if answer == "yes":
            
                if self.name == "Z" and int(self.pos) >= 45000 and newposition < 45000:
                    
                    xpos = self.master.x.pos
                    self.master.x.runmotor(-600)
                    ypos = self.master.y.pos
                    self.master.y.runmotor(3500)
                    rpos = self.master.r.pos
                    self.master.r.runmotor(-1800)
                    
                elif int(self.master.z.pos) < 5800:
                    
                    if self.checkrellimits(newposition) == False:
                        messagebox.showerror("Out of Range", "Value set for this motor violates relative limits. Check positions of other motors and retry.")
                        return
                           
                self.runmotor(newposition)   
                
                if self.name == "Z" and int(self.pos) >= 45000 and newposition < 45000 and self.master.positioncall == False:
                        
                    self.master.x.runmotor(xpos)
                    self.master.y.runmotor(ypos)
                    self.master.r.runmotor(rpos)
                    
            self.master.overridebutton.deselect()
             
                    
        elif self.master.reloverridevar.get():
            
            if self.limits[0] <= newposition <= self.limits[1]:
          
                answer = messagebox.askquestion("Caution: Relative limit override", "Override of relative motor limits is selected. Are you sure you want to proceed without checking limits? Only click YES if you are sure that target Z-position can be safely reached with the current X,Y and R position.")
            
                if answer == "yes":
                    self.runmotor(newposition)
                
            else:
            
                messagebox.showerror("Out of Range", "Value set for this motor is out of range. Motor absolute limits are: {} ({})".format(self.limits,self.unitlimits))
                
            self.master.reloverridebutton.deselect()
                    
   
        else:
    
            if self.limits[0] <= newposition <= self.limits[1]:
                
                if self.name == "Z" and int(self.pos) >= 45000 and newposition < 45000:
                    
                    xpos = self.master.x.pos
                    self.master.x.runmotor(-600)
                    ypos = self.master.y.pos
                    self.master.y.runmotor(3000)
                    rpos = self.master.r.pos
                    self.master.r.runmotor(-1800)
                    
                elif int(self.master.z.pos) < 5800:
                    
                    if self.checkrellimits(newposition) == False:
                        messagebox.showerror("Out of Range", "Value set for this motor violates relative limits. Check positions of other motors and retry.")
                        return
                    
                self.runmotor(newposition)
                    
                        
                if self.name == "Z" and int(self.pos) >= 45000 and newposition < 45000 and self.master.positioncall == False:
                        
                    self.master.x.runmotor(xpos)
                    self.master.y.runmotor(ypos)
                    self.master.r.runmotor(rpos)
                                          
            else:
                        
                messagebox.showerror("Out of Range", "Value set for this motor is out of range. Motor absolute limits are: {} ({})".format(self.limits,self.unitlimits))
                
                
                
    def checkrellimits(self,newposition):
    
        if self.name == "X":
            if not -2600 < newposition < 1400:
                return False
                
        if self.name == "R":
            if not -1800 - (int(self.master.y.pos) - 2700)/5 < newposition < -1800 + (int(self.master.y.pos) - 2700)/5:
                return False
        
        if self.name == "Y":
            if newposition < 2700 + abs(int(self.master.r.pos) + 1800)*5:
                return False
                
        return True
                    
                    
                    
                    
    def runmotor(self, newposition):
    
        self.master.running = False
        
        time.sleep(0.2)
                
        inputstring = "RUNA,{}\r\n".format(newposition)
        self.motor.write(inputstring.encode("utf-8"))
        response = self.motor.readline().decode("utf-8").split(",")
        if len(response) > 2:
                if response[2][:-2] in self.master.errorcodes:
                    errormsg = "Motor {}: {} ({})\n".format(self.name,response[2][:-2],self.master.errorcodes[response[2][:-2]])
                else:
                    errormsg = "Motor {}: {}\n".format(self.name,response[2][:-2])
                self.master.errorlog.insert(tk.END, errormsg)
                
        self.master.running = True
            
    
    
    
    def stopmotor(self):
    
        self.master.running = False
        
        time.sleep(0.05)
    
        self.motor.write("STOP\r\n".encode("utf-8"))
        lastline = self.motor.readline().decode("utf-8")
        
        self.master.running = True
        
        
        
        
    def clearerror(self):
    
        self.master.running = False
        
        self.motor.write("CLR\r\n".encode("utf-8"))
        lastline = self.motor.readline().decode("utf-8")
        
        self.master.running = True
        
        
        
    
    def emergencystop(self):
    
        self.master.running = False
        time.sleep(0.02)
        
        self.motor.write("ESTOP\r\n".encode("utf-8"))
        lastline = self.motor.readline().decode("utf-8")
        
        self.startbutton.configure(state=tk.DISABLED)
        self.stopbutton.configure(state=tk.DISABLED)
     
        self.master.running = True
     
     
            
    def querymovement(self):
    
        self.master.running = False
        
        self.motor.write("SER\r\n".encode("utf-8"))
        response = self.motor.readline().decode("utf-8").split(",")
        
        self.master.running = True
        
        statusflag = response[0]
        binstatus = bin(int(statusflag[2:], base=16))
        
        if binstatus[-7] == "1":
            
            return False
            
        elif binstatus[-7] == "0":
        
            return True
        
       
       

if __name__ == "__main__":

    root = MotorApp()
    root.mainloop()