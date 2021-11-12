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

        self.statusframe = tk.Frame(self, height=300, width=350)
        self.statusframe.pack(side=tk.LEFT,padx=5)
        self.statusframe.pack_propagate(0)

        self.controlframe = tk.Frame(self, height=300, width=480)
        self.controlframe.pack(side=tk.LEFT, padx=5)
        self.controlframe.pack_propagate(0)

        self.menuframe = tk.Frame(self, height=300, width=200)
        self.menuframe.pack(side=tk.LEFT, padx=5)
        self.menuframe.pack_propagate(0)
        
        self.xlimits = (-5000,5000)
        self.ylimits = (-4500,4500)
        self.zlimits = (0,80000)
        self.rlimits = (-3600,3600)
        
        self.errorcodes = {"-1": "Stop motor first", "-2": "Invalid argument", "-3": "Cannot query this option", "-5": "Action failed due to internal error", "-6": "Command unavailable in current mode", "-7": "Motor is disabled", "-101": "Wrong argument type", "-102": "Invalid number of arguments"}

        self.today = date.today()
        
        self.portnum = 2
        
        self.connectbutton = tk.Button(self.controlframe, text="Connect to motors", command=self.portconnect)
        self.connectbutton.pack(side=tk.TOP)


    
    def portconnect(self):
    
        if self.portnum == 5:
        
            self.portnum += 1
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
            result = messagebox.askyesnocancel("Out of sync","The position information stored on motors does not match the current position file. Last position on file (saved on {}) is: X: {}, Y: {}, Z: {}, R: {}. Last position on motors is: X: {}, Y: {}, Z: {}, R: {}. Would you like to overwrite current file position with motor position? If yes, click YES. If you would like to use file position instead, click NO (this will override motor saved positions). Else click CANCEL, program will be closed and position file opened for edit.".format(current["date"],current["X"],current["Y"],current["Z"],current["R"],xselfloc,yselfloc,zselfloc,rselfloc))
        
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

        self.x = Motor(self,"X",self.xport,xpos,self.xlimits)
        self.y = Motor(self,"Y",self.yport,ypos,self.ylimits)
        self.z = Motor(self,"Z",self.zport,zpos,self.zlimits)  
        self.r = Motor(self,"R",self.rport,rpos,self.rlimits)
        
    
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
        succesfulmoves = 0
        
        self.running = False
        
        self.x.moveto(setposition["X"])
        self.y.moveto(setposition["Y"])
        self.z.moveto(setposition["Z"])
        self.r.moveto(setposition["R"])
                
        self.running = True
        
        
    
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

    def __init__(self,master,name,unit,position,limits):
    
        
        self.name = name
        self.motor = unit
        self.limits = limits
        self.master = master
        self.pos = position
        
        self.guiinit()
        
        
    
    def guiinit(self):
    
        self.frame = tk.Frame(self.master.controlframe)
        self.Label = tk.Label(self.frame, text="Motor {}".format(self.name), font=("Helvetica",12))
        self.Label.pack(side=tk.LEFT, padx=(0,5))
        self.poslabel = tk.Label(self.frame, text=self.pos, font=("Helvetica",12), width=10)
        self.poslabel.pack(side=tk.LEFT, padx=5)
        self.entry = tk.Entry(self.frame)
        self.entry.pack(side=tk.LEFT, padx=5)
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
                    response = self.motor.readline().decode("utf-(").split(",")
                    self.pos = response[2][0:-5]
                except RecursionError:
                    self.pos = "Error"
            
                self.poslabel.configure(text=self.pos)
        
        
        
    def changeposition(self):

        try:
            self.newpos = int(self.entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a position to set")
            return
            
        if self.limits[0] <= self.newpos <= self.limits[1]:
        
            self.master.running = False
            time.sleep(0.1)
            
            inputstring = "RUNA,{}\r\n".format(self.newpos)
            self.motor.write(inputstring.encode("utf-8"))
            response = self.motor.readline().decode("utf-8").split(",")
            if len(response) > 2:
                if response[2][:-2] in self.master.errorcodes:
                    errormsg = "Motor {}: {} ({})\n".format(self.name,response[2][:-2],self.errorcodes[response[2][:-2]])
                else:
                    errormsg = "Motor {}: {}\n".format(self.name, response[2][:-2])
                self.master.errorlog.insert(tk.END, errormsg)
                
            self.master.running = True
            
            
        else:
        
            messagebox.showerror("Out of Range", "Value set for this motor is out of range. Motor range limits are: {}".format(self.limits))
            
            
            
    def moveto(self,newposition):
    
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
    
        self.motor.write("STOP\r\n".encode("utf-8"))
        lastline = self.motor.readline().decode("utf-8")
        
        self.master.running = True
        
        
        
    def clearerror(self):
    
        self.master.running = False
        
        self.motor.write("CLR\r\n".encode("utf-8"))
        lastline = self.motor.readline().decode("utf-8")
        
        self.master.running = True
        
        
    
    def emergencystop(self):
        
        self.motor.write("ESTOP\r\n".encode("utf-8"))
        lastline = self.motor.readline().decode("utf-8")
        
        self.startbutton.configure(state=tk.DISABLED)
        self.stopbutton.configure(state=tk.DISABLED)
     
     
            
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