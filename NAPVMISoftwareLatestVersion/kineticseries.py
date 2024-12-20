import tkinter as tk
import serial
import PySpin
import numpy
import ast
import os
import matplotlib
from tkinter import filedialog
from tkinter import messagebox
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SeriesGui(tk.Frame):


    def __init__(self,root,bnc,bncgui,system,camera,nodemap,streamnodemap,exposuretime,gain,delaysvector):

        tk.Frame.__init__(self,root)
        self.pack()

        self.root = root
        self.bnc = bnc
        self.bncgui = bncgui
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
        self.powermeasurement = False

        self.guiinit()



    def guiinit(self):

        self.leftframe = tk.Frame(self)
        self.leftframe.pack(side=tk.LEFT, padx=10)

        self.rightframe = tk.Frame(self)
        self.rightframe.pack(side=tk.LEFT, padx=10)

        self.description = tk.Message(self.leftframe, text="Kinetic series over a range of delays. Please specify delay range, increment and number of frames per delay.", font=("Helvetica",11), width=250)
        self.description.pack(side=tk.TOP, pady=10)
        
        self.settingsframe = tk.Frame(self.leftframe)
        self.settingsframe.pack(side=tk.TOP, pady=10)
        
        self.savesettings = tk.Button(self.settingsframe, text="Save Settings", command=self.experimentsaver)
        self.savesettings.pack(side=tk.LEFT)
        
        self.loadsettings = tk.Button(self.settingsframe, text="Load Settings", command=self.experimentloader)
        self.loadsettings.pack(side=tk.LEFT)
        
        self.channellabel = tk.Label(self.leftframe, text="Channel to scan:", anchor=tk.NW, font=("Helvetica",12))
        self.channellabel.pack()

        self.channelname = tk.StringVar(self.leftframe)
        self.channeltuner = tk.OptionMenu(self.leftframe, self.channelname, "A", "B", "C", "D", "E", "F", "G", "H")
        self.channeltuner.pack(side=tk.TOP,pady=(10,20))
        
        self.timelabel = tk.Label(self.leftframe, text="Choose time range (micro or nanoseconds)", anchor=tk.NW, font=("Helvetica",12))
        self.timelabel.pack()
        
        self.timerange = tk.StringVar(self.leftframe)
        self.timetuner = tk.OptionMenu(self.leftframe, self.timerange, "us", "ns")
        self.timetuner.pack(side=tk.TOP,pady=(10,20))
        

        self.delayrangelabel = tk.Label(self.leftframe, text="Delay range (min 0 - max 9999):", font=("Helvetica",12))
        self.delayrangelabel.pack(side=tk.TOP, pady=(20,5))

        self.delayrangeframe = tk.Frame(self.leftframe)
        self.delayrangeframe.pack(side=tk.TOP)
        
        self.rangenumber = 1
        
        self.rangeframe = {}

        self.rangeframe[1] = tk.Frame(self.delayrangeframe)
        self.rangeframe[1].pack(side=tk.TOP)
        
        self.rangelower = {}
        self.rangestart = {}
        self.rangeupper = {}
        self.rangeend = {}

        self.rangelower[1] = tk.IntVar(self.rangeframe[1], value=0)
        self.rangestart[1] = tk.Entry(self.rangeframe[1], textvariable=self.rangelower[1], width=10)
        self.rangestart[1].pack(side=tk.LEFT)

        self.rangeupper[1] = tk.IntVar(self.rangeframe[1], value=2000)
        self.rangeend[1] = tk.Entry(self.rangeframe[1], textvariable=self.rangeupper[1], width=10)
        self.rangeend[1].pack(side=tk.LEFT)
        
        self.rangeadder = tk.Button(self.leftframe, text="Add delay range", command=lambda:self.addrange(self.rangenumber+1))
        self.rangeadder.pack(side=tk.TOP, pady=(20,5))
        
        self.rangeremover = tk.Button(self.leftframe, text="Remove delay range", command=lambda:self.removerange(self.rangenumber) ,state=tk.DISABLED)
        self.rangeremover.pack(side=tk.TOP, pady=(20,5))

        self.incrementlabel = tk.Label(self.leftframe, text="Delay scanning increment:", font=("Helvetica",12))
        self.incrementlabel.pack(side=tk.TOP, pady=(40,5))
        
        self.incrementframe = tk.Frame(self.leftframe)
        self.incrementframe.pack(side=tk.TOP)
        
        self.increment = {}
        self.incremententry = {}

        self.increment[1] = tk.IntVar(self.incrementframe, value=100)
        self.incremententry[1] = tk.Entry(self.incrementframe, textvariable=self.increment, width=10)
        self.incremententry[1].pack(side=tk.TOP, pady=(0,0))

        self.framenumberlabel = tk.Label(self.leftframe, text="Number of averaged frames per delay:", font=("Helvetica",12))
        self.framenumberlabel.pack(side=tk.TOP, pady=(30,5))

        self.sumframes = tk.IntVar(self.leftframe, value=10)
        self.framenumber = tk.Entry(self.leftframe, textvariable=self.sumframes, width=10)
        self.framenumber.pack(side=tk.TOP, pady=(0,20))
        
        self.thresholdlabel = tk.Label(self.leftframe,text="Threshold (individual frame)", font=("Helvetica",12))
        self.thresholdlabel.pack(side=tk.TOP,pady=(10,5))
        
        self.threshold = tk.IntVar(self.leftframe, value=0)
        self.thresholdentry = tk.Entry(self.leftframe,textvariable=self.threshold,width=10)
        self.thresholdentry.pack(side=tk.TOP,pady=(0,20))
        
        self.minusvar = tk.IntVar(self.leftframe, value=0)
        self.minuscheck = tk.Checkbutton(self.leftframe, text="Negative delays", variable=self.minusvar, onvalue=1, offvalue=0)
        self.minuscheck.pack(side=tk.TOP,pady=(10,20))
        
        self.powerlabel = tk.Label(self.leftframe, text="Laser power measurement", font=("Helvetica",12))
        self.powerlabel.pack(side=tk.TOP,pady=(10,5))
        
        self.powermeter = tk.Button(self.leftframe, text="Use power meter", command=self.connectfieldmax)
        self.powermeter.pack(side=tk.TOP,pady=(0,20))
        
        self.powerconnected = tk.Label(self.leftframe, text="Power meter not connected", font=("Helvetica",12))
        self.powerconnected.pack()
        
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
        
        
        
    def addrange(self,instance): 
            
        self.rangeframe[instance] = tk.Frame(self.delayrangeframe)
        self.rangeframe[instance].pack(side=tk.TOP)
            
        self.rangelower[instance] = tk.IntVar(self.rangeframe[instance], value=0)
        self.rangestart[instance] = tk.Entry(self.rangeframe[instance], textvariable=self.rangelower[instance], width=10)
        self.rangestart[instance].pack(side=tk.LEFT)

        self.rangeupper[instance] = tk.IntVar(self.rangeframe[instance], value=2000)
        self.rangeend[instance] = tk.Entry(self.rangeframe[instance], textvariable=self.rangeupper[instance], width=10)
        self.rangeend[instance].pack(side=tk.LEFT)
            
        self.increment[instance] = tk.IntVar(self.incrementframe, value=100)
        self.incremententry[instance] = tk.Entry(self.incrementframe, textvariable=self.increment[instance], width=10)
        self.incremententry[instance].pack(side=tk.TOP, pady=(0,0))
            
        self.rangeremover.configure(state=tk.NORMAL)
            
        self.rangenumber = instance
        
        
        
    def removerange(self,instance):
   
        self.rangeframe[instance].destroy()
        self.incremententry[instance].destroy()
        self.increment[instance].destroy()
       
        self.rangenumber = instance - 1
        
        if instance == 2:
            self.rangeremover.configure(state=tk.DISABLED)
            
            
    def connectfieldmax(self):
        
        self.FMII = fieldmax.FieldMax(r'C:\Program Files (x86)\Coherent\FieldMaxII PC\Drivers\Win10\FieldMax2Lib\x64\FieldMax2Lib.dll')
        try:
            self.FMII.openDriver()
        except OSError:
            messagebox.showerror("Error","Could not connect to FieldMaII")
            return
        
        self.fmserialno = self.FMII.get_SerialNumber()
        self.laserenergy = self.FMII.get_dataPoint()
        if self.laserenergy == 0:
            self.laserenergy = self.FMII.get_dataPoint()
        
        self.powerconnected.config(text="Power meter {} connected, {} J".format(self.fmserialno,self.laserenergy))
        self.powermeasurement = True
        self.powermeter.configure(state=tk.DISABLED)
            
            

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

        try:
            channelname = self.channelname.get()
        except ValueError:
            messagebox.showerror("Error", "Please choose a channel")
            self.startbutton.configure(state=tk.NORMAL)
            return
        self.channelnumber = self.channelnumbers[channelname]

        self.filename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose experiment file name", filetypes=(("numpy zip archive", "*.npz"),("All files", "*.*")))
        if not self.filename:
            return
        if self.filename[-4:] != ".npz":
            self.filename += ".npz"

        self.startbutton.configure(state=tk.DISABLED)

        self.parameterfilename = self.filename[:-4] + "_parameters.txt"
        
        self.energyfilename = self.filename[:-4] + "_energies.txt"
        
        if self.powermeasurement == True:
            self.energies = {}

        self.imageseries = {}

        self.delaylist = []
        self.totalintensities = []

        self.running = True
        self.stopbutton.pack(side=tk.TOP, pady=(20,10))
        
        for i in range(self.rangenumber):
        
            if i == 0:
                self.delayscanrange = numpy.arange(int(self.rangestart[1].get()), (int(self.rangeend[1].get()) + 1), int(self.incremententry[1].get()))
        
            else:
                newrange = numpy.arange(int(self.rangestart[i+1].get()), (int(self.rangeend[i+1].get()) + 1), int(self.incremententry[i+1].get()))
                self.delayscanrange = numpy.concatenate([self.delayscanrange,newrange])
        
        self.intensityvtime.set_xlim(self.delayscanrange[0]-5, self.delayscanrange[-1]+5)
        
        self.bncgui.channel.active = False
        
        self.root.lift()

        self.delayloop(0)

    

    def delayloop(self, index):
        
        i = self.delayscanrange[index]
        
        if i < 10 and self.timerange.get() == "ns":
            currentdelay = "0.00000000" + str(i) + "00"
        elif i < 100 and self.timerange.get() == "ns":
            currentdelay = "0.0000000" + str(i) + "00"
        elif i < 1000 and self.timerange.get() == "ns":
            currentdelay = "0.000000" + str(i) + "00"
        elif i < 10000 and self.timerange.get() == "ns":
            currentdelay = "0.00000" + str(i) + "00"
        elif i < 10 and self.timerange.get() == "us":
            currentdelay = "0.00000" + str(i) + "00000"
        elif i < 100 and self.timerange.get() == "us":
            currentdelay = "0.0000" + str(i) + "00000"
        elif i < 1000 and self.timerange.get() == "us":
            currentdelay = "0.000" + str(i) + "00000"
        elif i < 10000 and self.timerange.get() == "us":
            currentdelay = "0.00" + str(i) + "00000"
        else:
            messagebox.showerror("Error", "Invalid delay")
            self.startbutton.configure(state=tk.NORMAL)
            self.bncgui.channel.active = True
            return
                
       
        if self.minusvar.get() == 1:
            currentdelay = "-" + currentdelay

        inputstring = ":PULS{}:DEL {}\r\n".format(self.channelnumber,currentdelay)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")

        self.after(100)
        
        if self.powermeasurement == True:
            self.laserenergy = self.FMII.get_dataPoint()

        self.imageloop()

        if self.erroroccurrence == True:
            self.starbutton.configure(state=tk.NORMAL)
            self.stopbutton.pack_forget()
            self.bncgui.channel.active = True
            return 
            
        self.imageseries[str(i)] = self.sumimage
        self.delaylist.append(i)
        self.totalintensities.append(numpy.sum(self.sumimage))
        if self.powermeasurement == True:
            self.energies[str(i)] = self.laserenergy

        self.lastdelaydisplay.clear()
        self.lastdelaydisplay.imshow(self.sumimage, cmap="gray", vmin=0)
        self.intensityvtime.clear()
        self.intensityvtime.plot(self.delaylist, self.totalintensities)
        self.canvas.draw()

        if i < self.delayscanrange[-1] and self.running == True:
            index += 1
            self.after(10, self.delayloop, index)

        else:
            self.bncgui.channel.active = True
            self.savedata()


    
    def savedata(self):

        
        numpy.savez_compressed(self.filename, **self.imageseries)

        self.parameters = {"Exposure time": self.exposure, "Gain": self.gain, "Number of frames per delay": self.numberofframes, "Negative delays": self.minusvar, "Scan channel": self.channelname.get(), "Delay start": int(self.delayscanrange[0]), "Delay end": int(self.delayscanrange[-1]), "Delay A": self.delaysvector[0], "Delay B": self.delaysvector[1], "Delay C": self.delaysvector[2], "Delay E": self.delaysvector[3], "Delay F": self.delaysvector[4], "Delay G": self.delaysvector[5], "Delay H": self.delaysvector[6]}
        
        f = open(self.parameterfilename, "w")
        f.write(str(self.parameters))
        f.close
        
        if self.powermeasurement == True:
            f = open(self.energyfilename, "w")
            f.write(str(self.energies))
            f.close()
            
            messagebox.showinfo("Measurement finished", "Image has been saved under: {}, energy file under {}, parameters under {}".format(self.filename, self.energyfilename, self.parameterfilename))

        else:
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
        if filename[:-4] != ".txt":
            filename = filename + ".txt"
        
        rangelower = []
        rangeupper = []
        increments = []
       
        for i in range(self.rangenumber):
            rangelower.append(int(self.rangestart[i+1].get()))
            rangeupper.append(int(self.rangeend[i+1].get()))
            increments.append(int(self.incremententry[i+1].get()))
       
        experiment = {"channel": self.channelname.get(), "timerange": self.timerange.get(), "rangenumber": self.rangenumber, "rangelower": rangelower, "rangeupper": rangeupper, "increment": increments, "frameno": self.sumframes.get(), "threshold": int(self.thresholdentry.get()), "negative": self.minusvar.get()}
        
        f = open(filename, "w")
        f.write(str(experiment))
        f.close()
        
        
        
    def experimentloader(self):
        
        filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Open experiment settings:", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        f = open(filename, "r")
        experiment = ast.literal_eval(f.read())
        f.close()
    
        self.channelname.set(experiment["channel"])
        self.timerange.set(experiment["timerange"])
        
        while self.rangenumber < experiment["rangenumber"]:
            self.addrange(self.rangenumber+1)
            
        while self.rangenumber > experiment["rangenumber"]:
            self.removerange(self.rangenumber)
        
        for i in range(self.rangenumber):
            self.rangestart[i+1].delete(0,tk.END)
            self.rangestart[i+1].insert(0,experiment["rangelower"][i])
            self.rangeend[i+1].delete(0,tk.END)
            self.rangeend[i+1].insert(0,experiment["rangeupper"][i])
            self.incremententry[i+1].delete(0,tk.END)
            self.incremententry[i+1].insert(0,experiment["increment"][i])
            
        self.framenumber.delete(0,tk.END)
        self.framenumber.insert(0,experiment["frameno"])
        self.thresholdentry.delete(0,tk.END)
        self.thresholdentry.insert(0,experiment["threshold"])
        if experiment["negative"] == 1:
            self.minuscheck.select()
        else:
            self.minuscheck.deselect()
        


    def userinterrupt(self):

        if self.powermeasurement == True:
            self.FMII.closeDriver()
        
        self.running = False
        self.stopbutton.pack_forget()

