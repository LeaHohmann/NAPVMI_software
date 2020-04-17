import PySpin
import tkinter as tk
import cameramodule

system = PySpin.System.GetInstance()


root = tk.Tk()
root.geometry("300x200+30+30")

cameraconnect = tk.Button(root, text="Connect to Camera", command=lambda:cameramodule.camerainit(system,"18479311"))
cameraconnect.pack(ipadx=5, ipady=5)

quit = tk.Button(root, text="Quit", command=lambda:cameramodule.quitthecamera(system))
quit.pack(ipadx=5, ipady=5)

messageframe = tk.Frame(root, width=200)
messageframe.pack(side=tk.BOTTOM)

messagelabel = tk.Label(messageframe, text="")
messagelabel.pack

root.mainloop()


