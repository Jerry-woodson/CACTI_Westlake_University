from customtkinter import *


class StreamFrame(CTkFrame):
    def __init__(self, master=None):
        super().__init__(master=master, width=335, height=335, border_width=2)
        self.grid_propagate(False)
        self.image_panel = None

    def create_widget(self):
        self.image_panel = CTkLabel(self, text="")
        self.image_panel.grid(row=0, column=0)
