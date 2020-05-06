import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import numpy as np

class Application(tk.Tk):

    def __init__(self):

        self.arraysize = 1

        tk.Tk.__init__(self)

        self.label = tk.Label(self, text="Array size:")
        self.label.pack(side=tk.TOP, pady=(10,5))

        self.numberlabel = tk.Label(self, text=self.arraysize)
        self.numberlabel.pack(side=tk.TOP, pady=(0,20))

        #self.scrollframe = tk.Frame(self)
        #self.scrollframe.pack(side=tk.TOP, pady=(0,30))

        #self.scrollbar = tk.Scrollbar(self.scrollframe)
        #self.scrollbar.pack(side=tk.RIGHT)

        #self.listbox = tk.Listbox(self.scrollframe, selectmode=tk.SINGLE, height=1)
        #for i in [1,3,5,7,9]:
           # self.listbox.insert(tk.END, i)
        #self.listbox.pack(side=tk.LEFT)
        
        #self.listbox.config(yscrollcommand=self.scrollbar.set)
        #self.scrollbar.config(command=self.listbox.yview)

        self.variable = tk.IntVar(self)
        self.variable.set(1)

        self.dropdown = tk.OptionMenu(self, self.variable, 1, 3, 5, 7, 9)
        self.dropdown.pack(side=tk.TOP, pady=(0,30))

        self.incrementplus = tk.Button(self, text="+", command=self.plus)
        self.incrementplus.pack(side=tk.TOP, pady=(0,5))

        self.incrementminus = tk.Button(self, text="-", command=self.minus)
        self.incrementminus.pack(side=tk.TOP, pady=(0,30))
    
        self.savebutton = tk.Button(self, text="Save array", command=self.savearray)
        self.savebutton.pack(side=tk.TOP, pady=(0,10))


    def plus(self):

        self.increment = self.variable.get()
        self.arraysize += self.increment
        self.numberlabel.configure(text=self.arraysize)

    
    def minus(self):

        self.increment = self.variable.get()
        self.arraysize -= self.increment
        self.numberlabel.configure(text=self.arraysize)

    
    def savearray(self):

        self.array = np.arange(self.arraysize)
        self.filename = filedialog.asksaveasfilename(initialdir="C:/",title="Save array as:", filetypes=(("Text files","*.txt"),("All files","*.*")))
        np.savetxt(self.filename, self.array)



root = Application()
root.mainloop()

