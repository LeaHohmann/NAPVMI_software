import serial
import ast
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext as scroll
import datetime
from datetime import date


class MotorApp(tk.Tk):

    def _init_(self):

        tk.Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.quitgui)

        self.title("Motor control")

        self.motorstatus = {"X": 0, "Y": 0, "Z": 0, "R": 0}
        self.globalstatus = 0

        self.serialnumbers = {"X": <serialnumber>, "Y": <serialnumber>, "Z": <serialnumber>, "R": <serialnumber>}

        self.statusframe = tk.Frame(self)
        self.statusframe.pack(side=tk.LEFT)

        self.controlframe = tk.Frame(self)
        self.controlframe.pack(side=tk.LEFT)

        self.menuframe = tk.Frame(self)
        self.menuframe.pack(side=tk.LEFT)


        #Establish connection to all 4 motors (or call function), if off - error message and "Retry" button, if all on: Update status
        #Check if there is current.txt in the folder: 
            #If YES: load and ask user to confirm current position
            #If NO or user disagrees with position: Open determine position window (pre-entered from file, otherwise zero)
        #Load GUI (for all connected devices)


    
    def portconnect(self):
        
        try:
            string = "COM{}".format(portnum)
            self.port = serial.Serial(string,baudrate=115200,bytesize=8,parity="N",stopbits=1,timeout=30)
        except:
            portnum += 1
            self.portconnect()

        self.port.write("SER\r\n".encode("utf-8"))
        lastline = self.port.readline().decode("utf-8")
        
        if self.serialnumbers["X"] in lastline:

            self.x = self.port
            self.motorstatus["X"] = 1
            self.globalstatus += 1

        elif self.serialnumbers["Y"] in lastline:

            self.y = self.port
            self.motorstatus["Y"] = 1
            self.globalstatus += 1


        elif self.serialnumbers["Z"] in lastline:

            self.z = self.port
            self.motorstatus["Z"] = 1
            self.globalstatus += 1

        elif self.serialnumbers["R"] in lastline:

            self.r = self.port
            self.motorstatus["R"] = 1
            self.globalstatus += 1


        if self.globalstatus == 4:

            self.loadcurrent()
            
       
        elif portnum < 9:

            portnum += 1
            self.portconnect()

        else:

            string = ""

            for motor, stat in self.motorstatus.items():
                if stat == 0:
                    string += "{} ".format{motor}

            answer = messagebox.askretrycancel("Error:", "Motors {} could not be found".format(string))

            if answer:
                portnum = 1
                self.portconnect()

            else:
                self.closegui()

        
    
    
    def loadcurrent(self):
    
        f = open("current.txt", "r")
        current = ast.literal_eval(f.read())
        f.close()
        
        result = messagebox.askquestion("The last used position (saved on {}) is: X: {}, Y: {}, Z: {}, R: {}. Would you like to set this as current position (only click yes, if position has not been changed since then)? If no, the program will be closed and the position storage file will be opened for edit. Edit the position and run program again.".format(current["date"],current["X"],current["Y"],current["Z"],current["R"]))
        
        if result == "yes":
        
            self.xpos = current["X"]
            self.ypos = current["Y"]
            self.zpos = current["Z"]
            self.rpos = current["R"]
            self.guiinit()
            
        else:
        
            self.closegui
            
           
    
    
    def guiinit(self):


        #Status frame
        
        self.statusheader = tk.Label(self.statusframe, text="Error Log", font=("Helvetica",14))
        self.statusheader.pack(side=tk.TOP)
        
        self.errorlog = scroll.ScrolledText(self.statusframe, width = 50, height = 20, fond=("Courier",12))
        self.errorlog.pack(side=tk.TOP)
        
        
        #Control frame
        
        self.controlheader = tk.Label(self.controlframe, text="Motor control", font=("Helvetica",14))
        self.controlheader.pack(side=tk.TOP)
        
        self.xframe = tk.Frame(self.controlframe)
        self.xframe.pack(side=tk.TOP, pady=5)
        self.xLabel = tk.Label(self.xframe, text="Motor X", font=("Helvetica",12))
        self.xLabel.pack(side=tk.LEFT, padx=(0,5))
        self.xposlabel = tk.Label(self.xframe, text=self.xpos, font=("Helvetica",12))
        self.xposlabel.pack(side=tk.LEFT, padx=5)
        self.xentry = tk.Entry(self.xframe)
        self.xentry.pack(side=tk.LEFT, padx=5)
        self.xbutton = tk.Button(self.xframe, text="Set position", command=lambda: self.changeposition(self.x,"X"))
        self.xbutton.pack(side=tk.LEFT, padx=5)
        
        self.yframe = tk.Frame(self.controlframe)
        self.yframe.pack(side=tk.TOP, pady=5)
        self.yLabel = tk.Label(self.yframe, text="Motor Y", font=("Helvetica",12))
        self.yLabel.pack(side=tk.LEFT, padx=(0,5))
        self.yposlabel = tk.Label(self.yframe, text=self.ypos, font=("Helvetica",12))
        self.yposlabel.pack(side=tk.LEFT, padx=5)
        self.yentry = tk.Entry(self.yframe)
        self.yentry.pack(side=tk.LEFT, padx=5)
        self.ybutton = tk.Button(self.yframe, text="Set position", command=lambda: self.changeposition(self.y,"Y"))
        self.ybutton.pack(side=tk.LEFT, padx=5)
        
        self.zframe = tk.Frame(self.controlframe)
        self.zframe.pack(side=tk.TOP, pady=5)
        self.zLabel = tk.Label(self.zframe, text="Motor Z", font=("Helvetica",12))
        self.zLabel.pack(side=tk.LEFT, padx=(0,5))
        self.zposlabel = tk.Label(self.zframe, text=self.zpos, font=("Helvetica",12))
        self.zposlabel.pack(side=tk.LEFT, padx=5)
        self.zentry = tk.Entry(self.zframe)
        self.zentry.pack(side=tk.LEFT, padx=5)
        self.zbutton = tk.Button(self.zframe, text="Set position", command=lambda: self.changeposition(self.z,"Z"))
        self.zbutton.pack(side=tk.LEFT, padx=5)
        
        self.rframe = tk.Frame(self.controlframe)
        self.rframe.pack(side=tk.TOP, pady=5)
        self.rLabel = tk.Label(self.rframe, text="Motor R", font=("Helvetica",12))
        self.rLabel.pack(side=tk.LEFT, padx=(0,5))
        self.rposlabel = tk.Label(self.rframe, text=self.rpos, font=("Helvetica",12))
        self.rposlabel.pack(side=tk.LEFT, padx=5)
        self.rentry = tk.Entry(self.rframe)
        self.rentry.pack(side=tk.LEFT, padx=5)
        self.rbutton = tk.Button(self.rframe, text="Set position", command=lambda: self.changeposition(self.r,"R"))
        self.rbutton.pack(side=tk.LEFT, padx=5)


        #Menu frame
        
        self.menuheader = tk.Label(self.menuframe, text="Saved positions", font=("Helvetica",14))
        self.menuheader.pack(side=tk.TOP)
        
        self.favourites = tk.Listbox(self.menuframe)
        self.favourites.pack(side=tk.TOP, pady=10)
        
        self.setbutton = tk.Button(self.menuframe, text="Set chosen position", font=("Helvetica",14))
        self.setbutton.pack(side=tk.TOP)
        
        self.loadfavourites()
        
        
        
    def loadfavourites(self)
    
        #Load the favourite positions file and append all options to listbox



    def changeposition(self,motor,identifier):

        #Move motor to position entered by user (after checking limits and, if Z is moved a large distance, moving X and Y to zero)



    def emergencystop(self):

        #Execute emergency stop



    def setfavourite(self):

        #Move to chosen stored position one motor at a time


   
    def closegui(self):

        #Save current position to current.txt; save error log to log.txt

    
