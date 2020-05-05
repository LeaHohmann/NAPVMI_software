import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import tkSimpleDialog
import numpy as np

class Application(tk.Tk):

    def __init__(self):

        tk.Tk.__init__(self)

        self.label = tk.Label(self, text="Enter size of array to be saved:")
        self.label.pack(side=tk.TOP, pady=(10,20))

        self.getnumber = tk.Entry(self)
        self.getnumber.pack(side=tk.TOP, pady=(0,30))

        self.savebutton = tk.Button(self, text="Save array", command=self.savearray)
        self.savebutton.pack(side=tk.TOP, pady=(0,10))

    
    def savearray(self):

        self.userentry = self.getnumber.get()
        if self.userentry == "":
            messagebox.showerror("Error", "No size specified. Please set a size value")
            return

        else:
            self.size = int(self.userentry)
            self.array = np.arange(self.size)
            self.filename = filedialog.asksaveasfilename(initialdir="C:/",title="Save array as:", filetypes=(("Text files","*.txt"),("All files","*.*")))
            np.savetxt(self.filename, self.array)



root = Application()
root.mainloop()

