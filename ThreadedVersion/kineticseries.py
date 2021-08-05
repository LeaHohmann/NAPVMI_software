import tkinter as tk
import serial
import PySpin
import numpy
import matplotlib
from tkinter import filedialog
from tkinter import messagebox
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SeriesGui(tk.Frame):


    def __init__(self,root,bnc,system,camera,nodemap,streamnodemap,exposuretime,gain,delaysvector):

        tk.Frame.__init__(self,root)
        self.pack()

        self.root = root
        self.bnc = bnc
        self.system = system
        self.camera = camera
        self.nodemap = nodemap
        self.exposure = exposuretime
        self.gain = gain
        self.delaysvector = delaysvector

        node_bufferhandling = PySpin.CEnumerationPtr(streamnodemap.GetNode("StreamBufferHandlingMode"))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        self.channelnumbers = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}

        self.erroroccurrence = False

        self.guiinit()



    def guiinit(self):

        self.leftframe = tk.Frame(self)
        self.leftframe.pack(side=tk.LEFT, padx=10)

        self.rightframe = tk.Frame(self)
        self.rightframe.pack(side=tk.LEFT, padx=10)

        self.description = tk.Message(self.leftframe, text="Kinetic series over a range of delays. Please specify delay range, increment and number of frames per delay.", font=("Helvetica",11), width=250)
        self.description.pack(side=tk.TOP, pady=10)
        
        self.channellabel = tk.Label(self.leftframe, text="Channel to scan:", anchor=tk.NW, font=("Helvetica",12))
        self.channellabel.pack()

        self.channelname = tk.StringVar(self.leftframe)
        self.channeltuner = tk.OptionMenu(self.leftframe, self.channelname, "A", "B", "C", "D", "E", "F", "G", "H")
        self.channeltuner.pack(side=tk.TOP,pady=(20,5))

        self.delayrangelabel = tk.Label(self.leftframe, text="Delay range in nanoseconds (min 0 - max 4000):", font=("Helvetica",12))
        self.delayrangelabel.pack(side=tk.TOP, pady=(20,5))

        self.delayrangeframe = tk.Frame(self.leftframe)
        self.delayrangeframe.pack(side=tk.TOP)

        self.delayrangelower = tk.IntVar(self.delayrangeframe, value=0)
        self.delayrangestart = tk.Entry(self.delayrangeframe, textvariable=self.delayrangelower, width=10)
        self.delayrangestart.pack(side=tk.LEFT)

        self.delayrangeupper = tk.IntVar(self.delayrangeframe, value=2000)
        self.delayrangeend = tk.Entry(self.delayrangeframe, textvariable=self.delayrangeupper, width=10)
        self.delayrangeend.pack(side=tk.LEFT)

        self.incrementlabel = tk.Label(self.leftframe, text="Delay scanning increment:", font=("Helvetica",12))
        self.incrementlabel.pack(side=tk.TOP, pady=(40,5))

        self.increment = tk.IntVar(self.leftframe, value=100)
        self.incremententry = tk.Entry(self.leftframe, textvariable=self.increment, width=10)
        self.incremententry.pack(side=tk.TOP, pady=(0,20))

        self.framenumberlabel = tk.Label(self.leftframe, text="Number of averaged frames per delay:", font=("Helvetica",12))
        self.framenumberlabel.pack(side=tk.TOP, pady=(10,5))

        self.sumframes = tk.IntVar(self.leftframe, value=10)
        self.framenumber = tk.Entry(self.leftframe, textvariable=self.sumframes, width=10)
        self.framenumber.pack(side=tk.TOP, pady=(0,20))

        self.startbutton = tk.Button(self.leftframe, text="Start Acquisition", background="green", command=self.startacquisition)
        self.startbutton.pack(side=tk.TOP, pady=(50,10))

        self.stopbutton = tk.Button(self.leftframe, text="Interrupt Acquisition", background="red", command=self.userinterrupt)

        self.fig = matplotlib.figure.Figure(figsize=[4.6,7.2])
        self.grid = self.fig.add_gridspec(ncols=1, nrows=2)
        self.lastdelaydisplay = self.fig.add_subplot(self.grid[0,0])
        self.intensityvtime = self.fig.add_subplot(self.grid[1,0])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.rightframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH, pady=10)



    def startacquisition(self):

        self.node_triggermode = PySpin.CEnumerationPtr(self.nodemap.GetNode("TriggerMode"))
        self.node_triggermode.SetIntValue(1)

        try:
            self.numberofframes = int(self.framenumber.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter an integer number of frames")
            self.startbutton.configure(state=tk.NORMAL)
            return

        self.node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode("AcquisitionMode"))
        self.node_acquisitionmode.SetIntValue(2)
        self.node_framecount = PySpin.CIntegerPtr(self.nodemap.GetNode("AcquisitionFrameCount"))
        self.node_framecount.SetValue(self.numberofframes)

        channelname = self.channelname.get()
        self.channelnumber = self.channelnumbers[channelname]

        self.startbutton.configure(state=tk.DISABLED)

        self.filename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose experiment file name", filetypes=(("numpy zip archive", "*.npz"),("All files", "*.*")))
        if self.filename[-4:] != ".npz":
            self.filename += ".npz"

        self.parameterfilename = self.filename[:-4] + "_parameters.txt"

        self.root.attributes("-topmost","true")

        self.imageseries = {}

        self.delaylist = []
        self.totalintensities = []

        self.running = True
        self.stopbutton.pack(side=tk.TOP, pady=(20,10))

        self.intensityvtime.set_xlim(int(self.delayrangestart.get())-5, int(self.delayrangeend.get())+5)

        self.delayscanrange = numpy.arange(int(self.delayrangestart.get()), (int(self.delayrangeend.get()) + 1), int(self.incremententry.get()))

        self.delayloop(0)

    

    def delayloop(self, index):
        
        i = self.delayscanrange[index]
        
        if i < 1000:
            currentdelay = "0.000000" + str(i) + "00"
        elif i < 10000:
            currentdelay = "0.00000" + str(i) + "00"
        elif i < 100000:
            currentdelay = "0.0000" + str(i) + "00"
        elif i < 1000000:
            currentdelay = "0.000" + str(i) + "00"
        else:
            messagebox.showerror("Error", "Maximum delay is 1000000ns")
            self.startbutton.configure(state=tk.NORMAL)
            return

        inputstring = ":PULS{}:DEL {}\r\n".format(self.channelnumber,currentdelay)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")

        self.after(100)

        self.imageloop()

        if self.erroroccurrence == True:
            self.starbutton.configure(state=tk.NORMAL)
            self.stopbutton.pack_forget()
            return 
            
        self.imageseries[str(i)] = self.sumimage
        self.delaylist.append(i)
        self.totalintensities.append(numpy.sum(self.sumimage))

        self.lastdelaydisplay.clear()
        self.lastdelaydisplay.imshow(self.sumimage, cmap="gray", vmin=0)
        self.intensityvtime.clear()
        self.intensityvtime.plot(self.delaylist, self.totalintensities)
        self.canvas.draw()

        if i < int(self.delayrangeend.get()) and self.running == True:
            index += 1
            self.after(10, self.delayloop, index)

        else:
            self.savedata()


    
    def savedata(self):

        
        numpy.savez_compressed(self.filename, **self.imageseries)

        self.parameters = {"Exposure time": self.exposure, "Gain": self.gain, "Number of frames per delay": self.numberofframes, "Delay start": int(self.delayrangestart.get()), "Delay end": int(self.delayrangeend.get()), "Delay increment": int(self.incremententry.get()), "Delay A": self.delaysvector[0], "Delay B": self.delaysvector[1], "Delay C": self.delaysvector[2], "Delay E": self.delaysvector[3], "Delay F": self.delaysvector[4], "Delay G": self.delaysvector[5], "Delay H": self.delaysvector[6]}
        
        f = open(self.parameterfilename, "w")
        f.write(str(self.parameters))
        f.close

        messagebox.showinfo("Measurement finished", "Image has been saved under: {}, parameters under {}".format(self.filename, self.parameterfilename))

        self.startbutton.configure(state=tk.NORMAL)
        self.stopbutton.pack_forget()



    def imageloop(self):

        self.sumimage = numpy.zeros((964,1288), int)

        self.camera.BeginAcquisition()

        for i in range(self.numberofframes):

            try:
                image_result = self.camera.GetNextImage(2000)
                image_data = image_result.GetNDArray()
                self.sumimage += image_data
                image_result.Release()

            except PySpin.SpinnakerException as ex:
                self.camera.EndAcquisition()
                self.erroroccurrence = True
                messagebox.showerror("Error","{}".format(ex))
                return
            
        try:
            self.camera.EndAcquisition()
        except PySpin.SpinnakerException:
            pass



    def userinterrupt(self):

        self.running = False
        self.stopbutton.pack_forget()

