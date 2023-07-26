from customtkinter import *


class MeasurementFrame(CTkFrame):
    def __init__(self, master=None):
        super().__init__(master=master, width=335
                         , height=335,
                         border_width=2)
        self.grid_propagate(False)
        self.meas_panel = None

    def create_widget(self):
        self.meas_panel = CTkLabel(self, text="")
        self.meas_panel.grid(row=0, column=0)
