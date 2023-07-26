import customtkinter
import os
import tkinter as tk

from CameraControl.CameraController import CameraController
from DMDControl.DMDController import DMDController
from GUIWidgets.CameraFrame import CameraFrame
from GUIWidgets.DMDFrame import DMDFrame
from GUIWidgets.MeasurementFrame import MeasurementFrame
from GUIWidgets.ReconstructionFrame import ReconstructionFrame
from GUIWidgets.ResultFrame import ResultFrame
from GUIWidgets.StreamFrame import StreamFrame
from ModelControl.ModelController import ModelController
from customtkinter import *

customtkinter.deactivate_automatic_dpi_awareness()

class Application(CTk):
    def __init__(self):
        super().__init__()
        self.title("Camera + DMD v2.4")
        self.geometry('1920x1080')
        self.resizable(width=True, height=True)
        self.mask_pth = tk.StringVar()
        self.model_pth = tk.StringVar()  # 模型路径
        self.mask_pth.set(os.path.dirname(os.path.abspath(__file__)) + 'Masks')
        self.model_val = tk.StringVar()
        self.checkvar1 = tk.IntVar()
        self.triggercheck_val = tk.IntVar()

        # 初始化CameraController和CameraFrame
        self.cameracontroller = CameraController(master=self)
        self.cameraframe = CameraFrame(self, self.cameracontroller)
        self.cameraframe.create_widget()
        self.cameralabel = CTkLabel(self, width=20, height=1, text='相机操作', font=('华文宋体', 15, "bold"),
                                    anchor=customtkinter.N)

        # 初始化StreamFrame
        self.streamlabel = CTkLabel(self, width=15, height=1, text='相机串流', font=('华文宋体', 15, "bold"))
        self.streamframe = StreamFrame(self)
        self.streamframe.create_widget()

        # 为CameraController添加CameraFrame和StreamFrame的信息
        self.cameracontroller.set_streamframe(self.streamframe)
        self.cameracontroller.set_cameraframe(self.cameraframe)

        # 初始化MeasurementFrame
        self.measurementlabel = CTkLabel(self, width=15, height=1, text='测量值', font=('华文宋体', 15, "bold"))
        self.measurementframe = MeasurementFrame(self)
        self.measurementframe.create_widget()

        # 初始化ModelController
        self.modelcontroller = ModelController(meas_dir='Measurement', measurementframe=self.measurementframe,
                                               master=self)
        self.modelcontroller.init_model()

        # 初始化DMDController和DMDFrame
        self.dmdcontroller = DMDController(modelcontroller=self.modelcontroller)
        self.dmdframe = DMDFrame(self, self.dmdcontroller)
        self.dmdframe.create_widget()
        self.dmdlabel = CTkLabel(self, width=15, height=1, text='DMD操作', font=('华文宋体', 15, "bold"))
        self.dmdcontroller.set_dmdframe(self.dmdframe)

        # 初始化ResultFrame
        self.resultframe = ResultFrame(self)
        self.resultframe.create_widget()
        self.resultlabel = CTkLabel(self, width=15, height=1, text='重建结果', font=('华文宋体', 15, "bold"))

        # 初始化ReconstructionFrame
        self.reconstructionframe = ReconstructionFrame(self, modelcontroller=self.modelcontroller,
                                                       measurementframe=self.measurementframe,
                                                       resultframe=self.resultframe)
        self.reconstructionframe.grid_propagate(False)
        self.reconstructionframe.create_widget()
        self.reconstructionlabel = CTkLabel(self, width=15, height=1, text='重建画面', font=('华文宋体', 15, "bold"))

        # 布局调整
        self.cameralabel.place(x=140, y=6)
        self.cameraframe.place(x=50, y=26)

        self.streamlabel.place(x=470, y=6)
        self.streamframe.place(x=330, y=26)

        self.measurementlabel.place(x=470, y=450)
        self.measurementframe.place(x=330, y=490)

        self.reconstructionlabel.place(x=950, y=6)
        self.reconstructionframe.place(x=810, y=26)

        self.resultlabel.place(x=950, y=450)
        self.resultframe.place(x=740, y=490)

        self.dmdlabel.place(x=1480, y=6)
        self.dmdframe.place(x=1400, y=26)


if __name__ == '__main__':
    App = Application()
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    App.update()
    print("CameraFrame Geometry: {}".format(App.cameraframe.winfo_geometry()))
    print("StreamFrame Geometry: {}".format(App.streamframe.winfo_geometry()))
    print("ReconstructionFrame Geometry: {}".format(App.reconstructionframe.winfo_geometry()))
    print("DMDFrame Geometry: {}".format(App.dmdframe.winfo_geometry()))
    print("MeasurementFrame Geometry: {}".format(App.measurementframe.winfo_geometry()))
    print("ResultFrame Geometry: {}".format(App.resultframe.winfo_geometry()))
    App.mainloop()
