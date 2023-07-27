from customtkinter import *
from tkinter.filedialog import askdirectory

#初始化DMD
class DMDFrame(CTkFrame):
    def __init__(self, master=None, dmd=None):
        super().__init__(master=master, border_width=2)
        self.text_DDR = None
        self.label_DDR = None
        self.text_img8_num = None
        self.label_img8_num = None
        self.text_img2_num = None
        self.label_img2_num = None
        self.text_dmd_Model = None
        self.label_dmd_Model = None
        self.btn_link_dmd = None
        self.text_dmd_ip = None
        self.label_dmd_ip = None
        self.text_local_ip = None
        self.label_local_ip = None
        self.btn_send_mask = None
        self.btn_select_mask_pth = None
        self.btn_norm_mask = None
        self.btn_catch_mask = None
        self.btn_pause_dmd = None
        self.btn_stop_dmd = None
        self.btn_dmd_start = None
        self.label_loop_num = None
        self.text_compression_rate = None
        self.label_compression_rate = None
        self.text_begin_loc = None
        self.label_begin_loc = None
        self.text_loop_fre = None
        self.label_loop_fre = None
        self.label_trigger_fre = None
        self.text_loop_num = None
        self.text_trigger_fre = None
        self.dmd = dmd
    
    #创建功能button
    def create_widget(self):
        self.label_trigger_fre = CTkLabel(self, text='触发频率', width=15, height=1)
        self.label_trigger_fre.grid(row=1, column=0, pady=10)
        self.text_trigger_fre = CTkTextbox(self, width=80, height=1)
        self.text_trigger_fre.insert(1.0, '1')
        self.text_trigger_fre.grid(row=1, column=1, pady=10)

        self.label_loop_fre = CTkLabel(self, text='掩膜循环频率', width=15, height=1)
        self.label_loop_fre.grid(row=2, column=0)
        self.text_loop_fre = CTkTextbox(self, width=80, height=1)
        self.text_loop_fre.insert(1.0, '1')
        self.text_loop_fre.grid(row=2, column=1, pady=10)

        self.label_begin_loc = CTkLabel(self, text='循环开始位置', width=15, height=1)
        self.label_begin_loc.grid(row=3, column=0)
        self.text_begin_loc = CTkTextbox(self, width=80, height=1)
        self.text_begin_loc.insert(1.0, '1')
        self.text_begin_loc.grid(row=3, column=1, pady=10)

        self.label_compression_rate = CTkLabel(self, text='压缩比', width=15, height=1)
        self.label_compression_rate.grid(row=4, column=0)
        self.text_compression_rate = CTkTextbox(self, width=80, height=1)
        # self.text_compression_rate.insert(1.0, '10')
        self.text_compression_rate.grid(row=4, column=1, pady=10)

        self.label_loop_num = CTkLabel(self, text='循环图片张数', width=15, height=1)
        self.label_loop_num.grid(row=5, column=0)
        self.text_loop_num = CTkTextbox(self, width=80, height=1)
        self.text_loop_num.insert(1.0, '1')
        self.text_loop_num.grid(row=5, column=1, pady=10)

        self.btn_dmd_start = CTkButton(self, text='DMD开始播放', width=80, command=self.dmd.start_dmd, corner_radius=20)
        self.btn_dmd_start.grid(row=6, column=0, columnspan=2, pady=10)

        self.btn_stop_dmd = CTkButton(self, text='终止DMD', width=10, command=self.dmd.stop_dmd, corner_radius=20)
        self.btn_stop_dmd.grid(row=7, column=1, pady=10)

        self.btn_pause_dmd = CTkButton(self, text='暂停DMD', width=10, command=self.dmd.pause_dmd, corner_radius=20)
        self.btn_pause_dmd.grid(row=7, column=0, pady=10)

        self.btn_catch_mask = CTkButton(self, text='拍摄Mask', width=10, command=self.dmd.catch_mask, corner_radius=20)
        self.btn_catch_mask.grid(row=8, column=0, pady=10)

        self.btn_norm_mask = CTkButton(self, text='归一化Mask', width=8, command=self.dmd.norm_mask, corner_radius=20)
        self.btn_norm_mask.grid(row=8, column=1, pady=10, padx=5)

        self.btn_select_mask_pth = CTkButton(self, text='选择Mask路径', width=8,
                                             command=self.select_mask_pth, corner_radius=20)
        self.btn_select_mask_pth.grid(row=9, column=0, pady=10, padx=5)
        self.btn_send_mask = CTkButton(self, text='发送Mask', width=10, command=self.dmd.send_mask, corner_radius=20)
        self.btn_send_mask.grid(row=9, column=1, pady=10)

        # entry_mask_pth = tk.Entry(self, textvariable=mask_pth, state="readonly", width=40)
        # entry_mask_pth.grid(row=10, column=0, pady=10)

        self.label_local_ip = CTkLabel(self, text='Local IP', width=10, height=1)
        self.label_local_ip.grid(row=10, column=0, pady=10)
        self.text_local_ip = CTkTextbox(self, width=100, height=1)
        self.text_local_ip.insert(1.0, '192.168.1.10')
        self.text_local_ip.grid(row=10, column=1, pady=10)

        self.label_dmd_ip = CTkLabel(self, text='DMD IP', width=10, height=1)
        self.label_dmd_ip.grid(row=11, column=0, pady=10)
        self.text_dmd_ip = CTkTextbox(self, width=100, height=1)
        self.text_dmd_ip.insert(1.0, '192.168.1.20')
        self.text_dmd_ip.grid(row=11, column=1, pady=10)

        self.btn_link_dmd = CTkButton(self, text='Link DMD', width=80, command=self.dmd.link_dmd, corner_radius=20)
        self.btn_link_dmd.grid(row=12, column=0, columnspan=2, pady=10)

        self.label_dmd_Model = CTkLabel(self, text='DMD型号', width=10, height=1)
        self.label_dmd_Model.grid(row=13, column=0, pady=10)
        self.text_dmd_Model = CTkTextbox(self, width=80, height=1)
        self.text_dmd_Model.grid(row=13, column=1, pady=10)

        self.label_img2_num = CTkLabel(self, text='可存放2位图', width=10, height=1)
        self.label_img2_num.grid(row=14, column=0, pady=10)
        self.text_img2_num = CTkTextbox(self, width=80, height=1)
        self.text_img2_num.grid(row=14, column=1, pady=10)

        self.label_img8_num = CTkLabel(self, text='可存放8位图', width=10, height=1)
        self.label_img8_num.grid(row=15, column=0, pady=10)
        self.text_img8_num = CTkTextbox(self, width=80, height=1)
        self.text_img8_num.grid(row=15, column=1, pady=10)

        self.label_DDR = CTkLabel(self, text='可用内存', width=10, height=1)
        self.label_DDR.grid(row=16, column=0, pady=10)
        self.text_DDR = CTkTextbox(self, width=80, height=1)
        self.text_DDR.grid(row=16, column=1, pady=10)

        # message_box = CTkTextbox(message_Frame, width=70, height=20, bd=3, wrap='char')
        # message_box.grid(row=0, column=0)
        # message_box["state"] = DISABLED
    
    #选择mask路径
    def select_mask_pth(self):
        pth = askdirectory(initialdir=self.master.mask_pth.get())
        if pth == "":
            self.master.mask_pth.get()
        else:
            pth = pth.replace("/", "\\")
            self.master.mask_pth.set(pth)
    #获取DMD参数
    def set_dmd(self, dmd):
        self.dmd = dmd
