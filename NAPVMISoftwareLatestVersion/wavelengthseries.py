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
import ast
import os


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
        self.running = False

        self.guiinit()



    def guiinit(self):

        self.leftframe = tk.Frame(self)
        self.leftframe.pack(side=tk.LEFT, padx=10)

        self.rightframe = tk.Frame(self)
        self.rightframe.pack(side=tk.LEFT, padx=10)

        self.description = tk.Message(self.leftframe, text="Series over a range of wavelengths. Please specify wavelength range, increment, number of frames per wavelength and beam-laser delay for the experiment.", font=("Helvetica",11), width=250)
        self.description.pack(side=tk.TOP, pady=10)
        
        self.settingsframe = tk.Frame(self.leftframe)
        self.settingsframe.pack(side=tk.TOP, pady=10)
        
        self.savesettings = tk.Button(self.settingsframe, text="Save Settings", command=self.experimentsaver)
        self.savesettings.pack(side=tk.LEFT)
        
        self.loadsettings = tk.Button(self.settingsframe, text="Load Settings", command=self.experimentloader)
        self.loadsettings.pack(side=tk.LEFT)

        self.lambdarangelabel = tk.Label(self.leftframe, text="Wavelength range in nm (min 600 - max 665, use '.' for decimals):", font=("Helvetica",12))
        self.lambdarangelabel.pack(side=tk.TOP, pady=(20,5))

        self.lambdarangeframe = tk.Frame(self.leftframe)
        self.lambdarangeframe.pack(side=tk.TOP)
        
        self.rangeframes = {}
        self.lambdarangestart = {}
        self.lambdarangeend = {}
        
        self.rangeframes[1] = tk.Frame(self.lambdarangeframe)
        self.rangeframes[1].pack(side=tk.TOP)
        
        self.lambdarangestart[1] = tk.Entry(self.rangeframes[1], width=10)
        self.lambdarangestart[1].pack(side=tk.LEFT)

        self.lambdarangeend[1] = tk.Entry(self.rangeframes[1], width=10)
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
        
        self.incremententry = {}

        self.incremententry[1] = tk.Entry(self.incrementframe, width=10)
        self.incremententry[1].pack(side=tk.TOP)

        self.framenumberlabel = tk.Label(self.leftframe, text="Number of averaged frames per wavelength:", font=("Helvetica",12))
        self.framenumberlabel.pack(side=tk.TOP, pady=(10,5))

        self.sumframes = tk.IntVar(self.leftframe, value=10)
        self.framenumber = tk.Entry(self.leftframe, textvariable=self.sumframes, width=10)
        self.framenumber.pack(side=tk.TOP, pady=(0,20))

        self.delaylabel = tk.Label(self.leftframe, text="Beam - laser delay in microseconds (min 0 - max 6000):", font=("Helvetica",12))
        self.delaylabel.pack(side=tk.TOP, pady=(10,5))

        self.delay = tk.IntVar(self.leftframe, value=100)
        self.delayentry = tk.Entry(self.leftframe, textvariable=300, width=10)
        self.delayentry.pack(side=tk.TOP, pady=(0,20))
        
        self.channellabel = tk.Label(self.leftframe, text="Beam - laser delay channel", font=("Helvetica",12))
        self.channellabel.pack(side=tk.TOP, pady=(10,5))
        
        self.channelname = tk.StringVar(self.leftframe)
        self.channeltuner = tk.OptionMenu(self.leftframe, self.channelname, "A", "B", "C", "D", "E", "F", "G", "H")
        self.channeltuner.pack(side=tk.TOP,pady=(10,20))
        
        self.thresholdlabel = tk.Label(self.leftframe,text="Threshold (individual frame)", font=("Helvetica",12))
        self.thresholdlabel.pack(side=tk.TOP,pady=(10,5))
        
        self.threshold = tk.IntVar(self.leftframe, value=0)
        self.thresholdentry = tk.Entry(self.leftframe,textvariable=self.threshold,width=10)
        self.thresholdentry.pack(side=tk.TOP,pady=(0,20))

        self.startbutton = tk.Button(self.leftframe, text="Start Acquisition", background="green", command=self.startacquisition)
        self.startbutton.pack(side=tk.TOP, pady=(50,10))

        self.stopbutton = tk.Button(self.leftframe, text ="Interrupt Acquisition", background="red", command=self.userinterrupt)

        self.fig = matplotlib.figure.Figure(figsize=[4.6,7.2])
        self.grid = self.fig.add_gridspec(ncols=1, nrows=2)
        self.lastdelaydisplay = self.fig.add_subplot(self.grid[0,0])
        self.intensityvlambda = self.fig.add_subplot(self.grid[1,0])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.rightframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, expand=1, fill=tk.BOTH, pady=10)
        
        
    
    def addrange(self,instance):
    
        self.rangeframes[instance] = tk.Frame(self.lambdarangeframe)
        self.rangeframes[instance].pack(side=tk.TOP)

        self.lambdarangestart[instance] = tk.Entry(self.rangeframes[instance], width=10)
        self.lambdarangestart[instance].pack(side=tk.LEFT)

        self.lambdarangeend[instance] = tk.Entry(self.rangeframes[instance], width=10)
        self.lambdarangeend[instance].pack(side=tk.LEFT)
        
        self.incremententry[instance] = tk.Entry(self.incrementframe, width=10)
        self.incremententry[instance].pack(side=tk.TOP)

        self.rangeremover.configure(state=tk.NORMAL)
        
        self.rangenumber = instance
        
        
    def removerange(self,instance):
    
        self.rangeframes[instance].destroy()
        self.increment[instance].destroy()
        
        self.rangenumber = instance-1
        
        if instance == 2:
            self.rangeremover.configure(state=tk.DISABLED)


    def evalentry(self):
    
        self.falsestart = False

        try:
            self.numberofframes = int(self.framenumber.get())
        except (KeyError, ValueError):
            self.wrongentry("Please enter an integer number of frames")
            return

        try:
            self.usdelay = int(self.delayentry.get())
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
            self.currentdelay = "-0.000" + str(self.usdelay) + "00000"
            inputstring = ":PULS{}:DEL {}\r\n".format(self.channelnumber,self.currentdelay)
            self.bnc.write(inputstring.encode("utf-8"))
            self.bnc.reset_input_buffer()

        elif self.usdelay <= 6000:
            self.currentdelay = "-0.00" + str(self.usdelay) + "00000"
            inputstring = ":PULS{}:Del {}\r\n".format(self.channelnumber,self.currentdelay)
            self.bnc.write(inputstring.encode("utf-8"))
            self.bnc.reset_input_buffer()

        else:
            self.wrongentry("Please choose a delay between 0 and 6000us")
            return
            
        self.stops = []
        self.incrementfund = []
        
        for i in self.rangeframes.keys():
        
            try:
                self.stops.append(decimal.Decimal(str(self.lambdarangestart[i].get())))
                self.stops.append(decimal.Decimal(str(self.lambdarangeend[i].get())))
            except KeyError:
                self.wrongentry("Please enter a valid start and stop wavelength")
                return

            if self.stops[-2] < 600 or self.stops[-1] > 670:
                self.wrongentry("Wavelength bounds are out of range. Please enter values between 600 and 670nm")
                return

            if self.stops[-2] > self.stops[-1]:
                self.wrongentry("Start wavelength cannot be larger than end wavelength")
                return

            try:
                self.incrementfund.append(decimal.Decimal(str(self.incremententry[i].get())))
            except KeyError:
                self.wrongentry("Enter wavelength increment in nm")
                return

            if self.incrementfund[-1] < decimal.Decimal("0.001") or self.incrementfund[i-1] > decimal.Decimal(1):
                self.wrongentry("Increment out of range (min 0.001, max 1nm)")
                return
                
        self.iterations = len(self.stops)/2



    def wrongentry(self,message):

        messagebox.showerror("Error",message)
        self.startbutton.configure(state=tk.NORMAL)
        self.falsestart = True
     


    def startacquisition(self):

        self.node_triggermode = PySpin.CEnumerationPtr(self.nodemap.GetNode("TriggerMode"))
        self.node_triggermode.SetIntValue(1)

        self.node_acquisitionmode = PySpin.CEnumerationPtr(self.nodemap.GetNode("AcquisitionMode"))
        self.node_acquisitionmode.SetIntValue(2)
        self.node_framecount = PySpin.CIntegerPtr(self.nodemap.GetNode("AcquisitionFrameCount"))
        self.numberofframes = self.sumframes.get()
        self.node_framecount.SetValue(self.numberofframes)

        self.startbutton.configure(state=tk.DISABLED)
        
        self.evalentry()
        if self.falsestart:
            return

        self.filename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose experiment file name", filetypes=(("numpy zip archive", "*.npz"),("All files", "*.*")))
        if self.filename[-4:] != ".npz":
            self.filename += ".npz"

        self.parameterfilename = self.filename[:-4] + "_parameters.txt"
        
        self.running = True
       
        self.imageseries = {}

        self.fundamentalist = []
        self.totalintensities = []

        self.intensityvlambda.set_xlim(self.stops[0] - decimal.Decimal(0.5), self.stops[-1] - decimal.Decimal(0.5))

        self.stopbutton.pack(side=tk.TOP, pady=(20,10))
        
        inputstring = "SL {}\r\n".format(str(self.stops[0]))
        self.laser.write(inputstring.encode("utf-8"))
        response = self.laser.read(2).decode("utf-8")
        self.laser.reset_input_buffer()
        if response != "OK":
            self.wrongentry("Problem occurred while setting wavelength.")
            return
        inputstring = "WL {}\r\n".format(str(self.incrementfund[0]))
        self.laser.write(inputstring.encode("utf-8"))
        respone = self.laser.read(2).decode("utf-8")
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

        self.wavelengthloop(0)
                


    def wavelengthloop(self,instance):
        
        self.laser.reset_input_buffer()
        inputstring = "GLC\r\n"
        self.laser.write(inputstring.encode("utf-8"))
        lastline = self.laser.readline().decode("utf-8")
        self.laser.reset_input_buffer()
        fundamental = decimal.Decimal(lastline[:-2])
        
        if self.stops[2*instance+1]-fundamental > self.incrementfund[instance]:
         
            inputstring = "LU\r\n"
            self.laser.write(inputstring.encode("utf-8"))
            response = self.laser.read(size=2).decode("utf-8")
            self.laser.reset_input_buffer()
            if response != "wl":
                self.wrongentry("Problem occurred while incrementing wavelength")
                print(response)
                self.erroroccurrence = True
                self.running = False
                return

            self.after(100)

            self.imageloop()

            if self.erroroccurrence == True:
                self.starbutton.configure(state=tk.NORMAL)
                self.stopbutton.pack_forget()
                return
                
            self.datahandling()
                
            if self.running:
                self.wavelengthloop(instance)
                
        elif instance < self.iterations-1:
            
            inputstring = "SL {}\r\n".format(str(self.stops[2*instance+1]))
            self.laser.write(inputstring.encode("utf-8"))
            response = self.laser.read(2).decode("utf-8")
            self.laser.reset_input_buffer()
            if response != "OK":
                self.wrongentry("Problem occurred while setting wavelength.")
                return
            inputstring = "WL {}\r\n".format(str(self.incrementfund[instance]))
            self.laser.write(inputstring.encode("utf-8"))
            respone = self.laser.read(2).decode("utf-8")
            self.laser.reset_input_buffer()
            if response != "OK":
                self.wrongentry("Problem occurred while setting increment")
                return
                
            self.after(100)

            self.imageloop()

            if self.erroroccurrence == True:
                self.starbutton.configure(state=tk.NORMAL)
                self.stopbutton.pack_forget()
                return
                
            self.datahandling()
            
            if self.running:
                self.wavelengthloop(instance+1)
              
        else:
            
            self.savedata()
            
            
    
    def datahandling(self):
    
        self.laser.reset_input_buffer()
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
        self.intensityvlambda.clear()
        self.intensityvlambda.plot(numpy.asarray(self.fundamentalist,float), self.totalintensities)
        self.canvas.draw()
            


    def savedata(self):

        
        numpy.savez_compressed(self.filename, **self.imageseries)
        
        startlist = []
        stoplist = []
        incrementlist = []
        
        for i in self.rangeframes.keys():
            startlist.append(self.lambdarangestart[i].get())
            stoplist.append(self.lambdarangeend[i].get())
            incrementlist.append(self.incremententry[i].get())

        self.parameters = {"Exposure time": self.exposure, "Gain": self.gain, "Number of frames per wavelength": self.numberofframes, "Wavelength start": startlist, "Wavelength end": stoplist, "Wavelength increment": incrementlist, "Beam laser delay": self.delayentry.get()}
        
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
                if int(self.thresholdentry.get()) > 0:
                    image_data = image_data*(image_data>int(self.thresholdentry.get()))
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



    def experimentsaver(self):
        
        filename = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save experiment settings:", filetypes=(("Text files", "*.txt"),("All files", "*.*")))
        if filename[-4:] != ".txt":
            filename = filename + ".txt"
        
        rangelower = []
        rangeupper = []
        increments = []
        
        for i in range(self.rangenumber):
            rangelower.append(str(self.lambdarangestart[i+1].get()))
            rangeupper.append(str(self.lambdarangeend[i+1].get()))
            increments.append(str(self.incremententry[i+1].get()))
       
        experiment = {"rangenumber": self.rangenumber, "rangelower": rangelower, "rangeupper": rangeupper, "increment": increments, "frameno": int(self.sumframes.get()), "delaychannel": str(self.channelname.get()), "delay": int(self.delayentry.get()), "threshold": int(self.thresholdentry.get())}
        
        f = open(filename, "w")
        f.write(str(experiment))
        f.close()
        
        
        
    def experimentloader(self):
        
        filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Open experiment settings:", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        f = open(filename, "r")
        experiment = ast.literal_eval(f.read())
        f.close()
    
        self.channelname.set(experiment["delaychannel"])
        
        while self.rangenumber < experiment["rangenumber"]:
            self.addrange(self.rangenumber+1)
            
        while self.rangenumber > experiment["rangenumber"]:
            self.removerange(self.rangenumber)
        
        for i in range(self.rangenumber):
            self.lambdarangestart[i+1].delete(0,tk.END)
            self.lambdarangestart[i+1].insert(0,experiment["rangelower"][i])
            self.lambdarangeend[i+1].delete(0,tk.END)
            self.lambdarangeend[i+1].insert(0,experiment["rangeupper"][i])
            self.incremententry[i+1].delete(0,tk.END)
            self.incremententry[i+1].insert(0,experiment["increment"][i])
        
        self.framenumber.delete(0,tk.END)
        self.framenumber.insert(0,experiment["frameno"])
        self.delayentry.delete(0,tk.END)
        self.delayentry.insert(0,experiment["delay"])
        self.thresholdentry.delete(0,tk.END)
        self.thresholdentry.insert(0,experiment["threshold"])

        

    
    def userinterrupt(self):

        self.running = False
        self.stopbutton.pack_forget()
        self.startbutton.configure(state=tk.NORMAL)
        
    

