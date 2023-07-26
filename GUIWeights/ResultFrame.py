from customtkinter import *
import customtkinter
customtkinter.deactivate_automatic_dpi_awareness()
class ResultFrame(CTkFrame):
    def __init__(self, master=None):
        super().__init__(master=master, width=600
                         , height=240, border_width=2)
        self.grid_propagate(False)
        self.column_count = 0
        self.row_count = 0
        self.label_list = []

    def create_widget(self):
        for i in range(10):
            label = CTkLabel(self, text="")
            if self.column_count == 5:
                self.row_count += 1
                self.column_count = 0
            label.grid(row=self.row_count, column=self.column_count, padx=1, pady=1)
            self.column_count += 1
            self.label_list.append(label)
