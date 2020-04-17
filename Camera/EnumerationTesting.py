import PySpin
import tkinter as tk


def interfacedetection(system,label):
    
    interfacelist = system.GetInterfaces()
    interfacenumber = interfacelist.GetSize()
    label.configure(text="I detected {} interfaces".format(interfacenumber))
    


def cameradetection(system,label):

    cameralist = system.GetCameras()
    cameranumber = cameralist.GetSize()
    label.configure(text="I detected {} camera(s)".format(cameranumber))


def quit():
    
    try:
        cameralist.Clear()
    except NameError:
        pass
    
    try: 
        interfacelist.Clear()
    except NameError:
        pass

    system.ReleaseInstance()
    root.quit()

def main():
    
    system = PySpin.System.GetInstance()

    root = tk.Tk()
    root.geometry("300x200+30+30")
    
    leftframe = tk.Frame(root)
    leftframe.pack(side=tk.LEFT)
    interfacebutton = tk.Button(leftframe, text="Search Interfaces", command=lambda:interfacedetection(system,interfacelabel))
    interfacebutton.pack(side=tk.TOP, ipadx=5, ipady=5)
    interfacelabel = tk.Label(leftframe, text="")
    interfacelabel.pack(side=tk.TOP, pady=10)
    rightframe = tk.Frame(root)
    rightframe.pack(side=tk.LEFT)
    camerabutton = tk.Button(rightframe, text="Search Cameras", command=lambda:cameradetection(system,cameralabel))
    camerabutton.pack(side=tk.TOP, ipadx=5, ipady=5)
    cameralabel = tk.Label(rightframe, text="")
    cameralabel.pack(side=tk.TOP, pady=10)


    root.mainloop()


if __name__ == '__main__':
    main()
