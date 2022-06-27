import tkinter as tk
import serial
import PySpin
import numpy
import matplotlib
from tkinter import filedialog
from tkinter import messagebox
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class IntegrationGui(tk.Frame):


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
        
        self.channelnumbers = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}

        self.erroroccurrence = False

        node_bufferhandling = PySpin.CEnumerationPtr(streamnodemap.GetNode("StreamBufferHandlingMode"))
        node_bufferhandling.SetIntValue(node_bufferhandling.GetEntryByName("NewestOnly").GetValue())

        self.guiinit()



    def guiinit(self):
        
        self.leftframe = tk.Frame(self)
        self.leftframe.pack(side=tk.LEFT, padx=10)

        self.rightframe = tk.Frame(self)
        self.rightframe.pack(side=tk.LEFT, padx=10)

        self.description = tk.Message(self.leftframe, text="Integrates over a range of delays. Please specify delay range, increment and number of frames per delay.", font=("Helvetica",11), width=250)
        self.description.pack(side=tk.TOP, pady=10)
        
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

        self.delayrangelabel = tk.Label(self.leftframe, text="Delay range (min 100 - max 10000):", font=("Helvetica",12))
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
        
        self.minusvar = tk.IntVar(self.leftframe, value=0)
        self.minuscheck = tk.Checkbutton(self.leftframe, text="Negative delays", variable=self.minusvar, onvalue=1, offvalue=0)
        self.minuscheck.pack(side=tk.TOP,pady=(10,20))

        self.startbutton = tk.Button(self.leftframe, text="Start Acquisition", background="green", command=self.startacquisition)
        self.startbutton.pack(side=tk.TOP, pady=(50,10))

        self.stopbutton = tk.Button(self.leftframe, text="Interrupt Acquisition", background="red", command=self.userinterrupt)

        self.fig = matplotlib.figure.Figure(figsize=[4.6,7.2])
        self.grid = self.fig.add_gridspec(ncols=1, nrows=2)
        self.integrateddisplay = self.fig.add_subplot(self.grid[0,0])
        self.lastdelaydisplay = self.fig.add_subplot(self.grid[1,0])

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

        try:
            channelname = self.channelname.get()
        except ValueError:
            messagebox.showerror("Error", "Please choose a channel")
            self.startbutton.configure(state=tk.NORMAL)
            return
        self.channelnumber = self.channelnumbers[channelname]
        
        self.startbutton.configure(state=tk.DISABLED)

        self.filename = filedialog.asksaveasfilename(initialdir="C:/", title="Choose image file name", filetypes=(("binary numpy array file","*.npy"),("All files","*.*")))
        if not self.filename:
            return
        if self.filename[-4:] != ".npy":
            self.filename += ".npy"

        self.parameterfilename = self.filename[:-4] + "_parameters.txt"

        self.root.attributes("-topmost","true")

        self.delayscanrange = numpy.arange(int(self.delayrangestart.get()), (int(self.delayrangeend.get()) + 1), int(self.incremententry.get()))
                
        self.integratedimage = numpy.zeros((964,1288), int)

        self.running = True
        self.stopbutton.pack(side=tk.TOP, pady=(20,10))
        
        self.bncgui.channel.active = False

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
          
          
        inputstring = ":PULS{}:DEL {}\r\n".format(self.channelnumber, currentdelay)
        self.bnc.write(inputstring.encode("utf-8"))
        lastline = self.bnc.readline().decode("utf-8")

        self.after(100)

        self.imageloop()

        if self.erroroccurrence == True:
            self.startbutton.configure(state=tk.NORMAL)
            self.stopbutton.pack_forget()
            self.bncgui.channel.active = True
            return 

        self.integratedimage += self.sumimage
        self.integrateddisplay.clear()
        self.integrateddisplay.imshow(self.integratedimage, cmap="gray", vmin=0)
        self.lastdelaydisplay.clear()
        self.lastdelaydisplay.imshow(self.sumimage, cmap="gray", vmin=0)
        self.canvas.draw()

        if i < int(self.delayrangeend.get()) and self.running == True:
            index += 1
            self.after(10, self.delayloop, index)

        else:
            self.bncgui.channel.active = True
            self.savedata()



    def savedata(self):

        numpy.save(self.filename, self.integratedimage)

        self.parameters = {"Exposure time": self.exposure, "Gain": self.gain, "Number of frames per delay": str(self.numberofframes), "Delay start": int(self.delayrangestart.get()), "Delay end": int(self.delayrangeend.get()), "Delay increment": int(self.incremententry.get()), "Delay A": self.delaysvector[0], "Delay C": self.delaysvector[1], "Delay D": self.delaysvector[2], "Delay E": self.delaysvector[3], "Delay F": self.delaysvector[4], "Delay G": self.delaysvector[5], "Delay H": self.delaysvector[6]}
        
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
                image_result = self.camera.GetNextImage(5000)
                image_data = image_result.GetNDArray()
                self.sumimage += image_data

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
        
        rangelower = int(self.delayrangestart.get())
        rangeupper = int(self.delayrangeend.get())
        increments = int(self.incremententry.get())
     
        experiment = {"channel": self.channelname.get(), "timerange": self.timerange.get(), "rangelower": rangelower, "rangeupper": rangeupper, "increment": increments, "frameno": self.sumframes.get(), "threshold": int(self.thresholdentry.get()), "negative": self.minusvar.get()}
        
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
        
        self.delayrangestart.delete(0,tk.END)
        self.delayrangeend.delete(0,tk.END)
        self.incremententry.delete(0,tk.END)
        self.delayrangestart.insert(0,experiment["rangelower"])
        self.delayrangeend.insert(0,experiment["rangeupper"])
        self.incremententry.insert(0,experiment["increment"]) 
            
        self.framenumber.delete(0,tk.END)
        self.framenumber.insert(0,experiment["frameno"])
        self.thresholdentry.delete(0,tk.END)
        self.thresholdentry.insert(0,experiment["threshold"])
        if experiment["negative"] == 1:
            self.minuscheck.select()
        else:
            self.minuscheck.deselect()
    
    

    def userinterrupt(self):

        self.running = False
        self.stopbutton.pack_forget()
    

