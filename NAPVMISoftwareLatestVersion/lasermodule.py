import serial
import tkinter as tk
from tkinter import messagebox
import decimal



class LaserApp(tk.Frame):

    def __init__(self, root, laser):

        self.laser = laser
        
        decimal.getcontext().prec = 8

        self.stepvalues = {"1 nm": "3.000", "100 pm": "0.300", "10 pm": "0.030", "5 pm": "0.015"}

        tk.Frame.__init__(self,root)
        self.pack()

        self.initialquery()
        self.guiinit()
        


    def initialquery(self):

        self.wavelength = ""

        inputstring = "GLC\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        lastline = self.laser.readline().decode("utf-8")
        self.fundamental = lastline[:-2]
        self.wavelength = decimal.Decimal(self.fundamental)/3



    def guiinit(self):

        self.laserlabel = tk.Label(self, text="Laser wavelength control", font=("Helvetica", 18), anchor=tk.NW)
        self.laserlabel.pack()

        self.wavelengthlabel = tk.Label(self, text="Current wavelength:", font=("Helvetica", 12))
        self.wavelengthlabel.pack(tk.TOP, padx=5, pady=(10,0))

        self.currentlambda = tk.Label(self, text=str(self.wavelength), font=("Helvetica", 12))
        self.currentlambda.pack(tk.TOP, padx=5, pady=(5,20))

        self.incrementplus = tk.Button(self, text="+", command=self.plus, font=("Arial", 12))
        self.incrementplus.pack(tk.LEFT, padx=5, pady=5)

        self.incrementminus = tk.Button(self, text=u"\u2212", command=self.minus, font=("Arial", 12))
        self.incrementminus.pack(tk.LEFT, padx=5, pady=5)

        self.step = tk.StringVar(self)

        self.stepdropdown = tk.OptionMenu(self, self.step, "1 nm", "100 pm", "10 pm", "5 pm")
        self.stepdropdown.pack(tk.LEFT, padx=5, pady=5)
        self.stepdropdown.configure(height=2)

        self.shutdownbutton = tk.Button(self, text="Shutdown laser controls", command=self.shutdown, font=("Helvetica",12))
        self.shutdownbutton.pack(tk.TOP, padx=5, pady=5)

    
    
    def guiupdate(self):

        self.wavelength = decimal.Decimal(self.fundamental)/3

        self.currentlambda.configure(text=str(self.wavelength))



    def plus(self):

        self.increment = 1
        self.changewavelength()



    def minus(self):

        self.increment = -1
        self.changewavelength()



    def changewavelength(self):

        inputstring = "GLC\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        lastline = self.laser.readline().decode("utf-8")
        
        if self.fundamental != lastline[:-2]:
            self.fundamental = lastline[:-2]
            self.guiupdate()
            messagebox.showinfo("Warning", "Wavelength out of sync due to manual change on the instrument. Wavelength was not changed, instead updated with current value. Check the current value and retry.")
            return

        try:
            self.stepvalue = self.stepvalues[self.step.get()]
            
            inputstring = "WL {}\r\n".format(self.stepvalue)
            self.laser.write(inputstring.encode("utf-8"))
            response = self.laser.read(2).decode("utf-8")
            self.laser.reset_input_buffer()

            if response != "OK":
                messagebox.showerror("Error", "Problem occurred when setting the wavelength increment.") 
                return

            if self.increment == 1:
                
                inputstring = "LU\r\n"
                self.laser.write(inputstring.encode("utf-8"))
                response = self.laser.read(2).decode("utf-8")
                self.laser.reset_input_buffer()

                if response != "OK":
                    messagebox.showerror("Error", "Problem occurred when setting wavelength. Please check resulting wavelength")

            elif self.increment == -1:

                inputstring = "LD\r\n"
                self.laser.write(inputstring.encode("utf-8"))
                response = self.laser.read(2).decode("uft-8")
                self.laser.reset_input.buffer()

                if response != "OK":
                    messagebox.showerror("Error", "Problem occurred when setting wavelength. Please check resulting wavelength.")

            inputstring = "GLC\r\n"
            self.laser.write(inputstring.encode("utf-8"))
            lastline = self.laser.readline().decode("utf-8")
            self.fundamental = lastline[:-2]
            self.guiupdate()


        except KeyError:
            messagebox.showerror("Error", "Please set an increment value and retry")



    def shutdown(self):

        inputstring = "SD\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        lastline = self.laser.read(2)
        if lastline == "OK":


