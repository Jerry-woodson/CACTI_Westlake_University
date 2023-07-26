import threading
import time
import tkinter

import customtkinter
from PIL import Image
from customtkinter import *

from utils import del_files, stop_thread

customtkinter.deactivate_automatic_dpi_awareness()


class ReconstructionFrame(CTkFrame):
    def __init__(self, master=None, modelcontroller=None, measurementframe=None, resultframe=None):
        super().__init__(master=master, width=335
                         , height=335, border_width=2
                         )
        self.grid_propagate(True)
        self.recon_panel = None
        self.btn_display_recon = None
        self.btn_recon = None
        self.modelcontroller = modelcontroller
        self.display_after_flag = None
        self.recon_after_flag = None
        self.new_file_list = []
        self.measurementframe = measurementframe
        self.resultframe = resultframe
        self.rst_counter = 0
        self.on_recon = False
        self.thread = None

    def create_widget(self):
        self.recon_panel = CTkLabel(self, text="")
        self.recon_panel.grid(row=1, column=0, columnspan=2)

        self.btn_display_recon = CTkButton(self, text='停止重建', width=15, command=self.stop_recon, corner_radius=20)
        self.btn_display_recon.grid(row=0, column=1, pady=10, padx=5)

        self.btn_recon = CTkButton(self, text='重建', width=15, command=self.start_recon_thread, corner_radius=20)
        self.btn_recon.grid(row=0, column=0, pady=10, padx=5)

    def refresh_recon(self):
        if self.master.dmdframe.text_compression_rate.get(1.0, tkinter.END) == '\n':
            tkinter.messagebox.showinfo("Info", "压缩比为空")
            self.stop_recon()
        compression_rate = int(self.master.dmdframe.text_compression_rate.get(1.0, tkinter.END))
        all_pics = os.listdir('./results')
        rst_path = 'results'
        for each in all_pics:
            if os.path.join(rst_path, each) not in self.new_file_list:
                file_path = os.path.join(rst_path, each)
                self.new_file_list.append(file_path)
        self.new_file_list.sort(key=lambda x: int(x[len(rst_path) + 8:-4]))  # result_1.bmp
        if len(self.new_file_list) != 0:
            for i in range(0, len(self.new_file_list), int(compression_rate / 10)):
                print(self.new_file_list[0])
                img = Image.open(self.new_file_list[0])
                img = CTkImage(img, size=(330, 330))
                self.recon_panel.configure(image=img)
                self.recon_panel.image = img

                rst_img = Image.open(self.new_file_list[0])
                rst_img = CTkImage(rst_img, size=(
                    120, 120))
                rst_idx = self.new_file_list[0][len(rst_path) + 8:-4]
                curr_label = self.resultframe.label_list[int(rst_idx)]
                curr_label.configure(image=rst_img)
                curr_label.image = rst_img

                del_files(self.new_file_list[0])
                self.new_file_list.pop(0)
                print(len(self.new_file_list))
                # update new_file_list
                self.new_file_list.sort(key=lambda x: int(x[len(rst_path) + 8:-4]))
                time.sleep(1)
        self.new_file_list = []

    def start_recon(self):
        self.on_recon = True
        while self.on_recon:
            self.modelcontroller.test(rotate_value=0)
            self.refresh_recon()
            time.sleep(1)

    def start_recon_thread(self):
        self.thread = threading.Thread(target=self.start_recon)
        self.thread.setDaemon(False)
        self.thread.start()

    def stop_recon(self):
        self.on_recon = False
        self.modelcontroller.set_meas_idx(1)
        if self.display_after_flag is not None:
            self.master.after_cancel(self.display_after_flag)
            self.btn_recon.after_cancel(self.recon_after_flag)
            for each in os.listdir('results'):
                os.remove(os.path.join('results', each))
            self.recon_panel.configure(image="")
            for each in self.resultframe.label_list:
                each.configure(image="")
            self.measurementframe.meas_panel.configure(image="")
            self.new_file_list = []
        else:
            for each in os.listdir('results'):
                os.remove(os.path.join('results', each))
            self.recon_panel.configure(image="")
            for each in self.resultframe.label_list:
                each.configure(image="")
            self.measurementframe.meas_panel.configure(image="")
            self.new_file_list = []
        stop_thread(self.thread)
        self.thread = None
