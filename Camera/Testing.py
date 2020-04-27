import tkinter as tk
import cameramodule


def quitgui():
    cameragui.quitthesystem()
    root.destroy()

root = tk.Tk()
root.geometry("500x400+30+30")
root.protocol("WM_DELETE_WINDOW", root.iconify)

cameragui = cameramodule.CameraApp(root,"18479311")

quit = tk.Button(root, text="Quit", command=quitgui)
quit.pack(side=tk.TOP, ipadx=5, ipady=5, pady=20)

root.mainloop()


