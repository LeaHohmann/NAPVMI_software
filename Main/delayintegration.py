import tkinter as tk
import serial
import PySpin
from tkinter import filedialog
from tkinter import messagebox


class IntegrationGui(tk.Toplevel):


    def __init__(self,root,bnc,system,camera,nodemap,exposuretime,gain,delaysvector,rootcameraframe,rootbncframe):

        tk.Toplevel.__init__(self,root)
        self.title("Acquisition: Delay integration")

        self.protocol("WM_DELETE_WINDOW", self.closegui)

        self.bnc = bnc
        self.system = system
        self.camera = camera
        self.nodemap = nodemap
        self.exposuretime = exposuretime
        self.gain = gain
        self.delaysvector = delaysvector
        self.rootbncframe = rootbndframe
        self.rootcameraframe = rootcameraframe

        self.guiinit()



    def guiinit(self):

        self.description = tk.Message(self, text="Integrates over a range of delays. Please specify delay range, increment and number of frames per delay.", font=("Helvetica",12))
        self.description.pack(side=tk.TOP, pady=10)

        self.delayrangelabel = tk.Label(self, text="Delay range in microseconds (min 0 - max 2000):", font=("Helvetica",12))
        self.delayrangelabel.pack(side=tk.TOP, pady=(20,5))

        self.delayrangelower = tk.IntVar(self, value=0)
        self.delayrangestart = tk.Entry(self, textvariable=self.delayrangelower, width=10)
        self.delayrangestart.pack(side=tk.LEFT)

        self.delayrangeupper = tk.IntVar(self, value=2000)
        self.delayrangeend = tk.Entry(self, textvariable=self.delayrangeupper, width=10)
        self.delayrangeend.pack(side=tk.LEFT)

        self.incrementlabel = tk.Label(self, text="Delay scanning increment:", font=("Helvetica",12))
        self.incrementlabel.pack(side=tk.TOP, pady=(40,5))

        self.increment = tk.IntVar(self, value=100)
        self.incremententry = tk.Entry(self, textvariable=self.increment, width=10)
        self.incremententry.pack(side=tk.TOP, pady=(0,20))

        self.framenumberlabel = tk.Label(self, text="Number of averaged frames per delay:", font=("Helvetica",12))
        self.framenumberlabel.pack(side=tk.TOP, pady=(10,5))

        self.sumframes = tk.IntVar(self, value=10)
        self.framenumber = tk.Entry(self, textvariable=self.sumframes, width=10)
        self.framenumber.pack(side=tk.TOP, pady=(0,20))

        self.startbutton = tk.Button(self, text="Start Acquisition", background="green", command=self.startacquisition)
        self.startbutton.pack(side=tk.TOP, pady=(50,10))



    def startacquisition(self):

        self.node_triggermode = PySpin.CEnumerationPtr(self.nodemap.GetNode("TriggerMode"))
        self.node_triggermode.SetIntValue(1) 

        self.filename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose image file name", filetypes=(("binary numpy array file","*.npy"),("All files","*.*")))
        self.parameterfilename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose parameter file name", filetypes=(("Text files","*.txt"),("All files","*.*")))

        delayscanrange = numpy.arange(self.delayrangelower, self.delayrangeupper + 1, self.increment)
        
        #make empty image

        for i in delayscanrange:
            self.imageloop(i)
            #add result to final image

        #save image under filaname
        #make dictionary for parameters
        #save parameters under parameter filename



    #imageloop function


    
    def closegui(self):

        self.rootbncframe.pack()
        self.rootcameraframe.pack()

        self.destroy()