import serial
import tkinter as tk
from tkinter import messagebox


class LaserApp(tk.Frame):

    def __init__(self, root, laser):

        self.laser = laser
        self.stepvalues = {"10 nm": 10000, "1 nm": 1000, "100 pm": 100, "10 pm": 10}

        tk.Frame.__init__(self,root)
        self.pack()

        self.initialquery()
        self.guiinit()
        


    def initialquery(self):

        self.wavelength = ""

        inputstring = "GLC\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        lastline = self.laser.readline().decode("utf-8")
        self.wavelength = lastline[:-2]



    def guiinit(self):

        self.laserlabel = tk.Label(self, text="Laser wavelength control", font=("Helvetica", 18), anchor=tk.NW)
        self.laserlabel.pack()

        self.wavelengthlabel = tk.Label(self, text="Current wavelength:", font=("Helvetica", 12))
        self.wavelengthlabel.pack(tk.TOP, padx=5, pady=(10,0))

        self.currentlambda = tk.Label(self, text=self.wavelength, font=("Helvetica", 12))
        self.currentlambda.pack(tk.TOP, padx=5, pady=(5,20))

        self.incrementplus = tk.Button(self, text="+", command=self.plus, font=("Arial", 12))
        self.incrementplus.pack(tk.LEFT, padx=5, pady=5)

        self.incrementminus = tk.Button(self, text=u"\u2212", command=self.minus, font=("Arial", 12))
        self.incrementminus.pack(tk.LEFT, padx=5, pady=5)

        self.step = tk.StringVar(self)

        self.stepdropdown = tk.OptionMenu(self, self.step, "10 nm", "1 nm", "100 pm", "10 pm")
        self.stepdropdown.pack(tk.LEFT, padx=5, pady=5)
        self.stepdropdown.configure(height=2)



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
        
        if self.laser != lastline[:-2]:
            self.laser = lastline[:-2]
            messagebox.showerror("Warning", "Wavelength out of sync due to manual change on the instrument. Wavelength was not changed, instead updated with current value. Check the current value and retry.")
            return

        try:
            self.stepvalue = self.stepvalues[self.step.get()]
            self.summand = self.stepvalue * self.increment
            self.newlambda = self.wavelength + self.summand
            if self.newlambda >= 240000 or self.newlambda <= 190000:
                messagebox.showerror("Error", "Value outside allowed wavelength range (190-240nm)")
                return

            else:
                #send the new wavelength to laser
                string = str(self.newlambda)

        except KeyError:
            messagebox.showerror("Error", "Please set an increment value and retry")

            

