import tkinter as tk
import serial
import PySpin
import numpy
import matplotlib
from tkinter import filedialog
from tkinter import messagebox
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import decimal


class WavelengthGui(tk.Frame):


    def __init__(self,root,bnc,laser,system,camera,nodemap,streamnodemap,exposuretime,gain,delaysvector):

        tk.Frame.__init__(self,root)
        self.pack()

        decimal.getcontext().prec = 8

        self.root = root
        self.bnc = bnc
        self.laser = laser
        self.system = system
        self.camera = camera
        self.nodemap = nodemap
        self.exposure = exposuretime
        self.gain = gain
        self.delaysvector = delaysvector
        
        self.channelnumbers = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}

        node_bufferhandling = PySpin.CEnumerationPtr(streamnodemap.GetNode("StreamBufferHandlingMode"))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        self.erroroccurrence = False

        self.guiinit()



    def guiinit(self):

        self.leftframe = tk.Frame(self)
        self.leftframe.pack(side=tk.LEFT, padx=10)

        self.rightframe = tk.Frame(self)
        self.rightframe.pack(side=tk.LEFT, padx=10)

        self.description = tk.Message(self.leftframe, text="Series over a range of wavelengths. Please specify wavelength range, increment, number of frames per wavelength and beam-laser delay for the experiment.", font=("Helvetica",11), width=250)
        self.description.pack(side=tk.TOP, pady=10)

        self.lambdarangelabel = tk.Label(self.leftframe, text="Wavelength range in nm (min 200 - max 230, use '.' for decimals):", font=("Helvetica",12))
        self.lambdarangelabel.pack(side=tk.TOP, pady=(20,5))

        self.lambdarangeframe = tk.Frame(self.leftframe)
        self.lambdarangeframe.pack(side=tk.TOP)
        
        self.rangeframes = {}
        self.lambdarangelower = {}
        self.lambdarangestart = {}
        self.lambdarangeupper = {}
        self.lambdarangeend = {}
        
        self.rangeframes[1] = tk.Frame(self.lambdarangeframe)
        self.rangeframes[1].pack(side=tk.TOP)

        self.lambdarangelower[1] = tk.StrVar(self.rangeframes[1], value="600.00000")
        self.lambdarangestart[1] = tk.Entry(self.rangeframes[1], textvariable=self.lambdarangelower, width=10)
        self.lambdarangestart[1].pack(side=tk.LEFT)

        self.lambdarangeupper[1] = tk.StrVar(self.rangeframes[1], value="603.00000")
        self.lambdarangeend[1] = tk.Entry(self.rangeframes[1], textvariable=self.lambdarangeupper, width=10)
        self.lambdarangeend[1].pack(side=tk.LEFT)
        
        self.rangenumber = 1
        
        self.rangeadder = tk.Button(self.leftframe, text="Add wavelength range", command=lambda:self.addrange(self.rangenumber+1))
        self.rangeadder.pack(side=tk.TOP, pady=(20,5))
        
        self.rangeremover = tk.Button(self.leftframe, text="Remove wavelength range", command=lambda:self.removerange(self.rangenumber) ,state=tk.DISABLED)
        self.rangeremover.pack(side=tk.TOP, pady=(20,5))

        self.incrementlabel = tk.Label(self.leftframe, text="Wavelength scanning increment in nm (min 0.001, max 1)", font=("Helvetica",12))
        self.incrementlabel.pack(side=tk.TOP, pady=(40,5))

        self.incrementframe = tk.Frame(self.leftframe)
        self.incrementframe.pack(side=tk.TOP)
        
        self.increment = {}
        self.incremententry = {}

        self.increment[1] = tk.StrVar(self.incrementframe, value=10)
        self.incremententry[1] = tk.Entry(self.incrementframe, textvariable=self.increment, width=10)
        self.incremententry[1].pack(side=tk.TOP, pady=(0,20))

        self.framenumberlabel = tk.Label(self.leftframe, text="Number of averaged frames per wavelength:", font=("Helvetica",12))
        self.framenumberlabel.pack(side=tk.TOP, pady=(10,5))

        self.sumframes = tk.IntVar(self.leftframe, value=10)
        self.framenumber = tk.Entry(self.leftframe, textvariable=self.sumframes, width=10)
        self.framenumber.pack(side=tk.TOP, pady=(0,20))

        self.delaylabel = tk.Label(self.leftframe, text="Beam - laser delay in microseconds (min 0 - max 6000):", font=("Helvetica",12))
        self.delaylabel.pack(side=tk.TOP, pady=(10,5))

        self.delay = tk.IntVar(self.leftframe, value=100)
        self.delayentry = tk.Entry(self.leftframe, textvariable=self.delayB, width=10)
        self.delayentry.pack(side=tk.TOP, pady=(0,20))
        
        self.channellabel = tk.Label(self.leftframe, text="Beam - laser delay channel", font=("Helvetica",12))
        self.channellabel.pack(side=tk.TOP, pady=(10,5))
        
        self.channelname = tk.StringVar(self.leftframe)
        self.channeltuner = tk.OptionMenu(self.leftframe, self.channelname, "A", "B", "C", "D", "E", "F", "G", "H")
        self.channeltuner.pack(side=tk.TOP,pady=(10,20))

        self.startbutton = tk.Button(self.leftframe, text="Start Acquisition", background="green", command=self.startacquisition)
        self.startbutton.pack(side=tk.TOP, pady=(50,10))

        self.stopbutton = tk.Button(self.leftframe, text ="Interrupt Acquisition", background="red", command=self.userinterrupt)

        self.fig = matplotlib.figure.Figure(figsize=[4.6,7.2])
        self.grid = self.fig.add_gridspec(ncols=1, nrows=2)
        self.lastdelaydisplay = self.fig.add_subplot(self.grid[0,0])
        self.intensityvtime = self.fig.add_subplot(self.grid[1,0])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.rightframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH, pady=10)
        
        
    
    def addrange(self,instance):
    
        self.rangeframes[instance] = tk.Frame(self.lambdarangeframe)
        self.rangeframes[instance].pack(side=tk.TOP)

        self.lambdarangelower[instance] = tk.StrVar(self.rangeframes[instance], value="603.00000")
        self.lambdarangestart[instance] = tk.Entry(self.rangeframes[instance], textvariable=self.lambdarangelower, width=10)
        self.lambdarangestart[instance].pack(side=tk.LEFT)

        self.lambdarangeupper[instance] = tk.StrVar(self.rangeframes[instance], value="606.00000")
        self.lambdarangeend[instance] = tk.Entry(self.rangeframes[instance], textvariable=self.lambdarangeupper, width=10)
        self.lambdarangeend[instance].pack(side=tk.LEFT)
        
        self.increment[instance] = tk.StrVar(self.incrementframe, value=10)
        self.incremententry[instance] = tk.Entry(self.incrementframe, textvariable=self.increment, width=10)
        self.incremententry[instance].pack(side=tk.TOP, pady=(0,20))

        self.rangeremover.configure(state=tk.NORMAL)
        
        self.rangenumber = instance
        
        
    def removerange(self,instance):
    
        self.rangeframes[instance].destroy()
        self.increment[instance].destroy()
        
        self.rangenumber = instance-1
        
        if instance == 2:
            self.rangeremover.configure(state=tk.DISABLED)


    def evalentry(self):

        try:
            self.numberofframes = int(self.framenumber.get())
        except (KeyError, ValueError):
            self.wrongentry("Please enter an integer number of frames")
            return

        try:
            self.usdelay = int(self.delayBentry.get())
        except KeyError:
            self.wrongentry("Please enter a molecular beam - laser delay")
            return
            
        try:
            channelname = self.channelname.get()
        except ValueError:
            messagebox.showerror("Error", "Please choose a channel")
            return
        self.channelnumber = self.channelnumbers[channelname]

        if self.usdelay <= 999:
            self.currentdelay = "-0.000" + str(self.usdelay)[1:] + "00000"
            inputstring = ":PULS{}:DEL {}\r\n".format(self.channelnumber,self.currentdelay)
            self.bnc.write(inputstring.encode("utf-8"))
            self.bnc.reset_input_buffer()

        elif self.usdelay <= 6000:
            self.currentdelay = "-0.00" + str(self.usdelay)[1:] + "00000"
            inputstring = ":PULS{}:Del {}\r\n".format(self.channelnumber,self.currentdelay)
            self.bnc.write(inputstring.encode("utf-8"))
            self.bnc.reset_input_buffer()

        else:
            self.wrongentry("Please choose a delay between 0 and 6000us")
            return
            
        self.startfund = {}
        self.stopfund = {}
        self.incrementfund = {}
        
        for i in self.rangeframe.keys():
        
            try:
                self.startfund[i] = decimal.Decimal(str(self.lambdarangestart[i].get()))
                self.stopfund[i] = decimal.Decimal(str(self.lambdarangeend[i].get()))
            except KeyError:
                self.wrongentry("Please enter a valid start and stop wavelength")
                return

            if self.startfund[i] < 600 or self.stopfund[i] > 670:
                self.wrongentry("Wavelength bounds are out of range. Please enter values between 600 and 670nm")
                return

            if self.startfund[i] > self.stopfund[i]:
                self.wrongentry("Start wavelength cannot be larger than end wavelength")
                return

            try:
                self.incrementfund[i] = decimal.Decimal(str(self.incremententry[i].get()))
            except KeyError:
                self.wrongentry("Enter wavelength increment in nm")
                return

            if self.incrementfund[i] < decimal.Decimal("0.001") or self.incrementfund[i] > decimal.Decimal(1):
                self.wrongentry("Increment out of range (min 0.001, max 1nm)")
                return



    def wrongentry(self,message):

        messagebox.showerror("Error",message)
        self.startbutton.configure(state=tk.NORMAL)
     


    def startacquisition(self):

        self.node_triggermode = PySpin.CEnumerationPtr(self.nodemap.GetNode("TriggerMode"))
        self.node_triggermode.SetIntValue(1)

        self.node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode("AcquisitionMode"))
        self.node_acquisitionmode.SetIntValue(2)
        self.node_framecount = PySpin.CIntegerPtr(self.nodemap.GetNode("AcquisitionFrameCount"))
        self.node_framecount.SetValue(self.numberofframes)

        self.startbutton.configure(state=tk.DISABLED)
        
        self.evalentry()

        self.filename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose experiment file name", filetypes=(("numpy zip archive", "*.npz"),("All files", "*.*")))
        if self.filename[-4:] != ".npz":
            self.filename += ".npz"

        self.parameterfilename = self.filename[:-4] + "_parameters.txt"
       
        self.imageseries = {}

        self.fundamentalist = []
        self.totalintensities = []

        self.intensityvtime.set_xlim(self.startfund[1] - decimal.Decimal(0.5), self.stopfund[len(self.rangeframes.keys())] - decimal.Decimal(0.5))

        running = True
        self.stopbutton.pack(side=tk.TOP, pady=(20,10))
        
        
        for i in self.rangeframe.keys():

            inputstring = "SL {}\r\n".format(str(self.startfund[i]))
            self.laser.write(inputstring.encode("utf-8"))
            response = self.laser.read(size=2).decode("utf-8")
            self.laser.reset_input_buffer()
            if response != "OK":
                self.wrongentry("Problem occurred while setting wavelength.")
                return
            inputstring = "WL {}\r\n".format(str(self.incrementfund[i]))
            self.laser.write(inputstring.encode("utf-8"))
            respone = self.laser.read(size=2).decode("utf-8")
            self.laser.reset_input_buffer()
            if response != "OK":
                self.wrongentry("Problem occurred while setting increment")
                return
    
            self.imageloop()

            inputstring = "GLC\r\n"
            self.laser.write(inputstring.encode("utf-8"))
            lastline = self.laser.readline().decode("utf-8")
            self.laser.reset_input_buffer()
            fundamental = decimal.Decimal(lastline[:-2])

            self.imageseries[str(fundamental)] = self.sumimage
            self.fundamentalist.append(str(fundamental))
            self.totalintensities.append(numpy.sum(self.sumimage))

            self.wavelengthloop(i)
                
            if running == False:
               break
            
        self.savedata()


    def wavelengthloop(self,instance):
            
        inputstring = "LU\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        response = self.laser.read(size=2).decode("utf-8")
        self.laser.reset_input_buffer()
        if response != "OK":
            self.wrongentry("Problem occurred while incrementing wavelength")
            self.erroroccurrence = True
            return

        self.after(100)

        self.imageloop()

        if self.erroroccurrence == True:
            self.starbutton.configure(state=tk.NORMAL)
            self.stopbutton.pack_forget()
            return
            
        inputstring = "GLC\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        lastline = self.laser.readline().decode("utf-8")
        self.laser.reset_input_buffer()
        fundamental = decimal.Decimal(lastline[:-2])

        self.imageseries[str(fundamental)] = self.sumimage
        self.fundamentalist.append(str(fundamental))
        self.totalintensities.append(numpy.sum(self.sumimage))

        self.lastdelaydisplay.clear()
        self.lastdelaydisplay.imshow(self.sumimage, cmap="gray", vmin=0)
        self.intensityvtime.clear()
        self.intensityvtime.plot(self.fundamentalist, self.totalintensities)
        self.canvas.draw()

        if fundamental < stopfund[i] and running == True:
            self.after(10, self.wavelengthloop)
        else:
            return     


    def savedata(self):

        
        numpy.savez_compressed(self.filename, **self.imageseries)

        inputstring = "PULS2:DEL?\r\n"
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")
        Bdelay = lastline[:-2]
        
        startlist = []
        stoplist = []
        incrementlist = []
        
        for i in self.rangeframes.keys():
            startlist.append(self.lambdarangestart[i].get())
            stoplist.append(self.lambdarangeend[i].get())
            incrementlist.append(self.incremententry[i].get())

        self.parameters = {"Exposure time": self.exposure, "Gain": self.gain, "Number of frames per wavelength": self.numberofframes, "Wavelength start": startlist, "Wavelength end": stoplist, "Wavelength increment": incrementlist, "Delay A": self.delaysvector[0], "Delay B": Bdelay, "Delay C": self.delaysvector[1], "Delay D": self.delaysvector[2], "Delay E": self.delaysvector[3], "Delay F": self.delaysvector[4], "Delay G": self.delaysvector[5], "Delay H": self.delaysvector[6]}
        
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
        self.startbutton.configure(state=tk.NORMAL)
        
    

