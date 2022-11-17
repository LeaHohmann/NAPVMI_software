import serial
import tkinter as tk
from tkinter import messagebox
import decimal
import threading
import time



class LaserApp(tk.Frame):

    def __init__(self, root, laser):

        self.laser = laser
        self.root = root
        
        decimal.getcontext().prec = 8

        self.stepvalues = {"1 nm": "1.000", "100 pm": "0.100", "10 pm": "0.010", "5 pm": "0.001"}

        tk.Frame.__init__(self,root)
        self.pack()

        self.initialquery()
        self.guiinit()
        
        self.active = True
        self.running = True
        
        t1 = threading.Thread(target=self.update)
        t1.daemon = True
        t1.start()
        


    def initialquery(self):

        inputstring = "GLC\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        lastline = self.laser.readline().decode("utf-8")
        self.fundamental = lastline[:-2]
        self.laser.reset_input_buffer()
        
        inputstring = "GP2\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        lastline = self.laser.readline().decode("utf-8")
        self.fcu1 = lastline[:-1]
        self.laser.reset_input_buffer()
        
        inputstring = "GP3\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        lastline = self.laser.readline().decode("utf-8")
        self.fcu2 = lastline[:-1]
        self.laser.reset_input_buffer()
     



    def guiinit(self):

        self.laserlabel = tk.Label(self, text="Laser control", font=("Helvetica", 18), anchor=tk.NW)
        self.laserlabel.pack()
        
        self.lambdaframe = tk.Frame(self)
        self.lambdaframe.pack(side=tk.TOP, pady=(5,20))

        self.wavelengthlabel = tk.Label(self.lambdaframe, text="Current wavelength:", font=("Helvetica", 12))
        self.wavelengthlabel.pack(side=tk.TOP, padx=5, pady=(10,0))

        self.currentlambda = tk.Label(self.lambdaframe, text=str(self.fundamental), font=("Helvetica", 12))
        self.currentlambda.pack(side=tk.TOP, padx=5, pady=(5,20))

        self.incrementplus = tk.Button(self.lambdaframe, text="+", command=self.plus, font=("Arial", 12))
        self.incrementplus.pack(side=tk.LEFT, padx=5, pady=5)

        self.incrementminus = tk.Button(self.lambdaframe, text=u"\u2212", command=self.minus, font=("Arial", 12))
        self.incrementminus.pack(side=tk.LEFT, padx=5, pady=5)

        self.step = tk.StringVar(self)

        self.stepdropdown = tk.OptionMenu(self.lambdaframe, self.step, "1 nm", "100 pm", "10 pm", "1 pm")
        self.stepdropdown.pack(side=tk.LEFT, padx=5, pady=5)
        self.stepdropdown.configure(height=2)
        
        self.fcu1frame = tk.Frame(self)
        self.fcu1frame.pack(side=tk.TOP, pady=(5,20))
        
        self.fcu1label = tk.Label(self.fcu1frame, text="FCU1 position", font=("Helvetica",12))
        self.fcu1label.pack(side=tk.TOP, padx=5, pady=(10,0))
        
        self.currentpos1 = tk.Label(self.fcu1frame, text=str(self.fcu1), font=("Helvetica",12))
        self.currentpos1.pack(side=tk.TOP, padx=5, pady=(10,0))
        
        self.fcu1plus = tk.Button(self.fcu1frame, text="+", command=lambda: self.fcuplus(1))
        self.fcu1plus.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.fcu1minus = tk.Button(self.fcu1frame, text="-", command=lambda: self.fcuminus(1))
        self.fcu1minus.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.fcu1step = tk.IntVar(self)
        
        self.fcu1stepdropdown = tk.OptionMenu(self.fcu1frame, self.fcu1step, 10, 20, 50, 100, 200, 500, 1000)
        self.fcu1stepdropdown.pack(side=tk.LEFT, padx=5, pady=5)
        self.fcu1stepdropdown.configure(height=2)
        
        self.fcu2frame = tk.Frame(self)
        self.fcu2frame.pack(side=tk.TOP, pady=(5,20))
        
        self.fcu2label = tk.Label(self.fcu2frame, text="FCU2 position", font=("Helvetica",12))
        self.fcu2label.pack(side=tk.TOP, padx=5, pady=(10,0))
        
        self.currentpos2 = tk.Label(self.fcu2frame, text=str(self.fcu2), font=("Helvetica",12))
        self.currentpos2.pack(side=tk.TOP, padx=5, pady=(10,0))
        
        self.fcu2plus = tk.Button(self.fcu2frame, text="+", command=lambda: self.fcuplus(2))
        self.fcu2plus.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.fcu2minus = tk.Button(self.fcu2frame, text="-", command=lambda: self.fcuminus(2))
        self.fcu2minus.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.fcu2step = tk.IntVar(self)
        
        self.fcu2stepdropdown = tk.OptionMenu(self.fcu2frame, self.fcu2step, 10, 20, 50, 100, 200, 500, 1000)
        self.fcu2stepdropdown.pack(side=tk.LEFT, padx=5, pady=5)
        self.fcu2stepdropdown.configure(height=2) 

        self.shutdownbutton = tk.Button(self, text="Shutdown laser controls", command=self.shutdown, font=("Helvetica",12))
        self.shutdownbutton.pack(side=tk.TOP, padx=5, pady=(20,5))

    
    
    def update(self):

        while self.active:
        
            time.sleep(0.5)
            
            if self.running:
                
                inputstring = "GLC\r\n"
                self.laser.write(inputstring.encode("utf-8"))
                lastline = self.laser.readline().decode("utf-8")
                self.fundamental = lastline[:-2]
                self.currentlambda.configure(text=self.fundamental)
                self.laser.reset_input_buffer()
                
                inputstring = "GP2\r\n"
                self.laser.write(inputstring.encode("utf-8"))
                lastline = self.laser.readline().decode("utf-8")
                self.fcu1 = lastline[:-1]
                self.currentpos1.configure(text=self.fcu1)
                self.laser.reset_input_buffer()
                
                inputstring = "GP3\r\n"
                self.laser.write(inputstring.encode("utf-8"))
                lastline = self.laser.readline().decode("utf-8")
                self.fcu2 = lastline[:-1]
                self.currentpos2.configure(text=self.fcu2)
                self.laser.reset_input_buffer()



    def plus(self):

        self.changewavelength(1)



    def minus(self):
        
        self.changewavelength(-1)



    def changewavelength(self,direction):

        self.running = False
        time.sleep(0.5)

        try:
            self.stepvalue = self.stepvalues[self.step.get()]
            
            inputstring = "WL {}\r\n".format(self.stepvalue)
            self.laser.write(inputstring.encode("utf-8"))
            response = self.laser.read(4).decode("utf-8")
            self.laser.reset_input_buffer()

            if direction == 1:
                
                inputstring = "LU\r\n"
                self.laser.write(inputstring.encode("utf-8"))
                response = self.laser.read(10).decode("utf-8")
                self.laser.reset_input_buffer()

            elif direction == -1:

                inputstring = "LD\r\n"
                self.laser.write(inputstring.encode("utf-8"))
                response = self.laser.read(10).decode("utf-8")
                self.laser.reset_input_buffer()

               
        except KeyError:
            messagebox.showerror("Error", "Please set an increment value and retry")    
            
        self.running = True
        
        
        
    def fcuplus(self,number):
    
        self.stepfcu(number,1)
        
    
    def fcuminus(self,number):
    
        self.stepfcu(number,-1)
        
        
        
    def stepfcu(self,number,direction):
    
        self.running = False
        time.sleep(0.5)
        
        if number == 1:
            stepwidget = self.fcu1step
            current = self.fcu1
        elif number == 2:
            stepwidget = self.fcu2step
            current = self.fcu2
        
        try:
            if direction == 1:
                newvalue = int(current) + stepwidget.get()
            elif direction == -1:
                newvalue = int(current) + stepwidget.get()
                
        except KeyError:
            messagebox.showerror("Error", "Please set an increment value and retry")
            
        inputstring = "MOVE{} {}\r\n".format(number,newvalue)
        self.laser.write(inputstring.encode("utf-8"))
        response = self.laser.read(2).decode("utf-8")
        self.laser.reset_input_buffer()

        if response != "OK":
            messagebox.showerror("Error", "Problem occurred when moving FCU motor. Please check resulting position and retry.")
        

        self.running = True
            


    def shutdown(self):

        inputstring = "SD\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        lastline = self.laser.read(2)
        if lastline != "OK":
            messagebox.showerror("Error", "Problem occurred during shutdown. Please retry")
        else:
            self.destroy()
            self.root.connectlaser.pack()


