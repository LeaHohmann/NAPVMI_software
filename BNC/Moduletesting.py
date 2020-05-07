import serial
import bncmodule
import tkinter as tk


class Root(tk.Tk):

    def __init__(self):

        tk.Tk.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self.quitgui)

        self.connect = tk.Button(self, text="Connect to Delay Generator", command=self.bncconnect)
        self.connect.pack(side=tk.TOP, ipadx=5, ipady=5, pady=10)
        
        
    def bncconnect(self):
        
        self.bnc = serial.Serial("COM5", baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=1)
        
        self.connect.destroy()
        self.bncinit()


    def bncinit(self):
        
        self.bncgui = bncmodule.DelayApp(self,self.bnc)
        

    def quitgui(self):

        try:
            self.bncgui.quitapp()
        except:
            pass
        
        self.bnc.close()
        self.quit()


root = Root()
root.mainloop()
