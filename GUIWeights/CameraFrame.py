import customtkinter

from utils import TxtWrapBy
from customtkinter import *


class CameraFrame(CTkFrame):

    def __init__(self, master=None, camera=None):
        super().__init__(master=master, border_width=2)
        self.btn_auto_adjust_exposure_time = None
        self.btn_burst_mode = None
        self.text_max_value = None
        self.label_height = None
        self.text_height = None
        self.text_offsety = None
        self.btn_restore_default_roi = None
        self.label_offsety = None
        self.text_offsetx = None
        self.text_width = None
        self.label_width = None
        self.text_gain = None
        self.label_gain = None
        self.label_us = None
        self.label_offsetx = None
        self.label_max_value = None
        self.btn_measurement = None
        self.text_exposure_time = None
        self.label_exposure_time = None
        self.label_Hz = None
        self.text_frame_rate = None
        self.label_frame_rate = None
        self.btn_set_parameter = None
        self.btn_get_parameter = None
        self.btn_save_jpg = None
        self.btn_save_bmp = None
        self.btn_stop_measurement = None
        self.btn_trigger_once = None
        self.checkbtn_trigger_software = None
        self.btn_stop_grabbing = None
        self.btn_start_grabbing = None
        self.radio_trigger = None
        self.radio_continuous = None
        self.btn_close_device = None
        self.btn_open_device = None
        self.btn_enum_devices = None
        self.text_burst_num = None
        self.master = master
        self.camera = camera
        self.device_list = None

    def create_widget(self):
        # 下拉条
        xVariable = customtkinter.StringVar()
        self.device_list = CTkComboBox(self, variable=xVariable, values=[], width=150)
        self.device_list.grid(row=0, column=0, columnspan=2, pady=10)
        self.device_list.bind("<<ComboboxSelected>>", self.xFunc)
        self.btn_enum_devices = CTkButton(self, text='枚举设备', width=80, command=self.camera.enum_devices,
                                          corner_radius=20)
        self.btn_enum_devices.grid(row=1, column=0, pady=10, columnspan=2)
        self.btn_open_device = CTkButton(self, text='打开设备', width=10, command=self.camera.open_device,
                                         corner_radius=20)
        self.btn_open_device.grid(row=5, column=0)
        self.btn_close_device = CTkButton(self, text='关闭设备', width=10, command=self.camera.close_device,
                                          corner_radius=20)
        self.btn_close_device.grid(row=5, column=1)

        self.radio_continuous = CTkRadioButton(self, text='Continuous', variable=self.master.model_val,
                                               value='continuous',
                                               width=15,
                                               height=1, command=self.camera.set_triggermode)
        self.radio_continuous.grid(row=6, column=0)
        self.radio_trigger = CTkRadioButton(self, text='触发模式', variable=self.master.model_val,
                                            value='triggermode', width=15,
                                            height=1, command=self.camera.set_triggermode)
        self.radio_trigger.grid(row=6, column=1, pady=10)
        self.master.model_val.set(1)

        self.btn_start_grabbing = CTkButton(self, text='开始取流', width=15,
                                            command=self.camera.start_grabbing, corner_radius=20)
        self.btn_start_grabbing.grid(row=7, column=0, pady=10)
        self.btn_stop_grabbing = CTkButton(self, text='停止取流', width=15,
                                           command=self.camera.stop_grabbing, corner_radius=20)
        self.btn_stop_grabbing.grid(row=7, column=1, pady=10)

        self.checkbtn_trigger_software = CTkCheckBox(self, text='通过软件触发',
                                                     variable=self.master.triggercheck_val,
                                                     onvalue=1,
                                                     offvalue=0)
        self.checkbtn_trigger_software.grid(row=8, column=0, pady=10)
        self.btn_trigger_once = CTkButton(self, text='触发一次', width=15, command=self.camera.trigger_once,
                                          corner_radius=20)
        self.btn_trigger_once.grid(row=8, column=1, pady=10)

        self.btn_save_bmp = CTkButton(self, text='保存为BMP', width=15, command=self.camera.bmp_save, corner_radius=20)
        self.btn_save_bmp.grid(row=9, column=0, pady=10)
        self.btn_save_jpg = CTkButton(self, text='保存为JPG', width=15, command=self.camera.jpg_save, corner_radius=20)
        self.btn_save_jpg.grid(row=9, column=1, pady=10)

        self.btn_get_parameter = CTkButton(self, text='获取相机参数', width=15,
                                           command=self.camera.get_parameter, corner_radius=20)
        self.btn_get_parameter.grid(row=10, column=0, pady=10, padx=10)
        self.btn_set_parameter = CTkButton(self, text='传递相机参数', width=15,
                                           command=self.camera.set_parameter, corner_radius=20)
        self.btn_set_parameter.grid(row=10, column=1, pady=10)

        self.label_frame_rate = CTkLabel(self, text='相机频率', width=15, height=1)
        self.label_frame_rate.grid(row=11, column=0, pady=10)
        self.text_frame_rate = CTkTextbox(self, width=80, height=1)
        self.text_frame_rate.grid(row=11, column=1, pady=10)
        # self.label_Hz = CTkLabel(self, text='Hz', width=5, height=1, bg_color="transparent")
        # self.label_Hz.grid(row=11, column=2, pady=10, sticky=W)

        self.label_exposure_time = CTkLabel(self, text='曝光时间', width=15, height=1)
        self.label_exposure_time.grid(row=12, column=0, pady=10)
        self.text_exposure_time = CTkTextbox(self, width=80, height=1, takefocus=1)
        self.text_exposure_time.grid(row=12, column=1, pady=10)
        # self.label_us = CTkLabel(self, text='us', width=5, height=1)
        # self.label_us.grid(row=12, column=1, pady=10)

        self.label_gain = CTkLabel(self, text='增益', width=15, height=1)
        self.label_gain.grid(row=13, column=0, pady=10)
        self.text_gain = CTkTextbox(self, width=80, height=1, takefocus=1)
        self.text_gain.grid(row=13, column=1, pady=10)

        self.label_offsetx = CTkLabel(self, text='水平偏移', width=15, height=1)
        self.label_offsetx.grid(row=14, column=0, pady=10)
        self.text_offsetx = CTkTextbox(self, width=80, height=1)
        self.text_offsetx.grid(row=14, column=1, pady=10)

        self.label_offsety = CTkLabel(self, text='垂直偏移', width=15, height=1)
        self.label_offsety.grid(row=15, column=0, pady=10)
        self.text_offsety = CTkTextbox(self, width=80, height=1)
        self.text_offsety.grid(row=15, column=1, pady=10)

        self.label_width = CTkLabel(self, width=10, height=1, text='宽度')
        self.label_width.grid(row=16, column=0, pady=10)
        self.text_width = CTkTextbox(self, width=80, height=1)
        self.text_width.grid(row=16, column=1, pady=10)

        self.label_height = CTkLabel(self, width=10, height=1, text='高度')
        self.label_height.grid(row=17, column=0, pady=10)
        self.text_height = CTkTextbox(self, width=80, height=1)
        self.text_height.grid(row=17, column=1, pady=10)

        self.btn_restore_default_roi = CTkButton(self, width=80, text='恢复初始ROI',
                                                 command=self.camera.restore_roi, corner_radius=20)
        self.btn_restore_default_roi.grid(row=18, column=0, pady=10, columnspan=2)
        self.label_max_value = CTkLabel(self, width=15, height=1, text='最大值')
        self.label_max_value.grid(row=19, column=0, pady=10)
        self.text_max_value = CTkTextbox(self, width=80, height=1)
        self.text_max_value.grid(row=19, column=1, pady=10)

        self.btn_burst_mode = CTkButton(self, text='连续拍摄', width=10, command=self.camera.burst, corner_radius=20)
        self.btn_burst_mode.grid(row=20, column=0, pady=10)
        self.text_burst_num = CTkTextbox(self, width=80, height=1)
        self.text_burst_num.grid(row=20, column=1, pady=10)

        self.btn_measurement = CTkButton(self, text='拍摄meas', width=15, command=self.camera.keep_burst,
                                         corner_radius=20)
        self.btn_measurement.grid(row=21, column=0, pady=10)
        self.btn_stop_measurement = CTkButton(self, text='停止拍摄', width=10,
                                              command=self.camera.stop_burst, corner_radius=20)
        self.btn_stop_measurement.grid(row=21, column=1, pady=10)

        self.btn_auto_adjust_exposure_time = CTkButton(self, text='自动调曝光', width=15,
                                                       command=self.camera.auto_adjust_exposure_time_threading,
                                                       corner_radius=20)
        self.btn_auto_adjust_exposure_time.grid(row=22, column=0, pady=10)

    # 绑定下拉列表至设备信息索引
    def xFunc(self):
        self.camera.nSelCamIndex = TxtWrapBy("[", "]", self.device_list.get())
