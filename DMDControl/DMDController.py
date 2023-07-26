import glob
import os
import socket
import sys
import time
import tkinter as tk

import cv2
import numpy as np


class DMDController:
    def __init__(self, dmdframe=None, modelcontroller=None):
        self.H_resolution = None
        self.V_resolution = None
        self.s = None
        self.DDR_NUM = None
        self.local = None
        self.dmd_type = None
        self.addr_ser = None
        self.imgDir = None
        self.Image_data_length = None
        self.dmdframe = dmdframe
        self.modelcontroller = modelcontroller

    def link_dmd(self):
        # DMD partqa
        addr_local = ("192.168.1.10", 1234)
        self.local = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.local.bind(addr_local)

        self.addr_ser = ("192.168.1.20", 1234)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 查询指令   80 80 80 80 F5 F5 F5 F5
        query_dmd = bytes([128, 128, 128, 128, 245, 245, 245, 245])  # 80   F5
        # 发送查询指令
        self.s.sendto(query_dmd, self.addr_ser)

        # u1接收到u2发来的消息
        query_dmd_recv = list(self.local.recv(1024))
        # 二进制图像存储数量
        imag2_nub = query_dmd_recv[8] * 256 * 256 * 256 + query_dmd_recv[9] * 256 * 256 + query_dmd_recv[10] * 256 + \
                    query_dmd_recv[11]  # 从第9个字节开始
        # 8位灰度图像存储数量
        imag8_nub = query_dmd_recv[13] * 256 * 256 + query_dmd_recv[14] * 256 + query_dmd_recv[15]

        # 获取DMD分辨率信息
        self.dmd_type = (query_dmd_recv[20] & 240) / 16
        if self.dmd_type == 0:
            self.dmdframe.text_dmd_Model.insert(1.0, '0.95 1920x1080')
            self.H_resolution = 2048  # 横向方向两边补充64bit 0 128
            self.V_resolution = 1080
        elif self.dmd_type == 1:
            self.dmdframe.text_dmd_Model.delete(1.0, tk.END)
            self.dmdframe.text_dmd_Model.insert(1.0, '0.7 XGA 1024x768')
            self.H_resolution = 1024
            self.V_resolution = 768
        elif self.dmd_type == 2:
            self.dmdframe.text_dmd_Model.delete(1.0, tk.END)
            self.dmdframe.text_dmd_Model.insert(1.0, '0.65 WXGA 1280x800\n')
            self.H_resolution = 1280
            self.V_resolution = 800
        elif self.dmd_type == 5:
            self.dmdframe.text_dmd_Model.delete(1.0, tk.END)
            self.dmdframe.text_dmd_Model.insert(1.0, '0.96 WUXGA 1920x1200\n')
            self.H_resolution = 2048  # 横向方向两边补充64bit 0
            self.V_resolution = 1200
        elif self.dmd_type == 7:
            self.dmdframe.text_dmd_Model.delete(1.0, tk.END)
            self.dmdframe.text_dmd_Model.insert(1.0, '0.55 XGA 1024x768\n')
            self.H_resolution = 1024
            self.V_resolution = 768
        elif self.dmd_type == 14:
            self.dmdframe.text_dmd_Model.delete(1.0, tk.END)
            self.dmdframe.text_dmd_Model.insert(1.0, '0.65 1920x1080\n')
            self.H_resolution = 2048  # 横向方向两边补充64bit
            self.V_resolution = 1080
        elif self.dmd_type == 15:
            self.dmdframe.text_dmd_Model.delete(1.0, tk.END)
            self.dmdframe.text_dmd_Model.insert(1.0, '0.9 WQXGA 2560x1600\n')
            self.H_resolution = 2560
            self.V_resolution = 1600
        # 内存条初始化信息||
        DDR_Init = query_dmd_recv[20] & 15
        if DDR_Init == 0:
            self.dmdframe.text_DDR.delete(1.0, tk.END)
            self.dmdframe.text_DDR.insert(1.0, '无可用内存！')
        else:
            if DDR_Init == 1 or DDR_Init == 2:
                self.dmdframe.text_DDR.delete(1.0, tk.END)
                self.dmdframe.text_DDR.insert(1.0, '可用内存1根！')
                self.DDR_NUM = 1
            if DDR_Init == 3:
                self.dmdframe.text_DDR.delete(1.0, tk.END)
                self.dmdframe.text_DDR.insert(1.0, '可用内存2根！')
                self.DDR_NUM = 2
        self.dmdframe.text_img2_num.insert(1.0, str(imag2_nub))
        self.dmdframe.text_img8_num.insert(1.0, str(imag8_nub))

    def send_mask(self):
        # ----------读取图片----------
        # 加载二值图像
        # 比如分辨率为1024*768图像占用内存空间为：1024*768/64/2=6144
        # 读入一副图像 2048*1080分辨率
        imgPath = self.dmdframe.master.mask_pth.get()  # 图像库路径
        self.imgDir = glob.glob(os.path.join(imgPath, '*.bmp'))  # 遍历所有bmp格式文件
        self.Image_data_length = self.H_resolution * self.V_resolution / 8
        Take_times = int(self.Image_data_length / 1024)  # （Take_times)*8=8192 bits 一次写1024字节 udp限制
        # 图像头数据
        Frame_image_data_Head = []
        Frame_image_data_Head[0:8] = [16, 16, 16, 16, 245, 245, 245, 245]  # 10   F5
        Frame_image_data_Head[8:16] = [0, 0, 0, 0, 0, 0, 0, 0]  # 10   F5
        vec = np.array([128, 64, 32, 16, 8, 4, 2, 1]).T
        for i in range(len(self.imgDir)):
            P0 = cv2.imread(self.imgDir[i], -1)  # 读取每张图片
            P0 = np.pad(P0, [(0, 0), (64, 64)], 'constant')
            P0 = (P0 / 255).astype(np.uint8)
            P0 = P0.reshape(-1, 8)  # 便于逐行写入
            P1 = np.matmul(P0, vec)
            P1 = np.array(P1).reshape(-1, 1024)

            # 写入第图像头
            self.s.sendto(bytes(Frame_image_data_Head), self.addr_ser)
            # 发送图像数据
            for j in range(Take_times):
                self.s.sendto(bytes(list(P1[j])), self.addr_ser)
            img_recv = list(self.local.recv(1024))
            # 改变图像写入地址
            add_dat = int(self.Image_data_length * (i + 1) / self.DDR_NUM / 8)
            add_4 = add_dat & 255
            add_3 = (add_dat >> 8) & 255
            add_2 = (add_dat >> 16) & 255
            add_1 = (add_dat >> 24) & 255
            Frame_image_data_Head[8:16] = [0, 0, 0, 0, add_1, add_2, add_3, add_4]
        # Add_Info('图片加载完成，共{}张'.format(len(imgDir)))

    def catch_mask(self):
        self.pause_dmd()
        self.stop_dmd()

        self.dmdframe.master.model_val.set('triggermode')
        self.dmdframe.master.cameracontroller.set_triggermode()

        self.dmdframe.text_trigger_fre.delete(1.0, tk.END)
        self.dmdframe.text_trigger_fre.insert(1.0, '1')  # 切换一张mask，发送一个触发信号

        self.dmdframe.master.cameracontroller.get_parameter()
        self.dmdframe.text_loop_fre.delete(1.0, tk.END)
        self.dmdframe.text_loop_fre.insert(1.0, '1')  # 每0.1秒捕捉一张mask

        self.dmdframe.text_loop_num.delete(1.0, tk.END)
        self.dmdframe.text_loop_num.insert(1.0, str(len(self.imgDir)))

        # self.dmdframe.text_compression_rate.delete(1.0, tk.END)
        # self.dmdframe.text_compression_rate.insert(1.0, str(len(self.imgDir) - 2))

        self.dmdframe.text_begin_loc.delete(1.0, tk.END)
        self.dmdframe.text_begin_loc.insert(1.0, '1')
        self.start_dmd()

        self.dmdframe.master.cameracontroller.obj_cam_operation.burst_mask_num = len(self.imgDir)

        # Add_Info('图片正在采集......')

    def norm_mask(self):

        self.pause_dmd()
        self.stop_dmd()
        self.dmdframe.master.model_val.set('continuous')
        self.dmdframe.master.cameracontroller.set_triggermode()
        # Add_Info('图片采集完成！')

        rank = []
        MP_pth = glob.glob(os.path.join(sys.path[0] + '\\Masks_photo', '*.bmp'))
        print(MP_pth)
        for i in range(len(MP_pth)):
            img = cv2.imread(MP_pth[i], -1)
            img = img.astype(np.uint8)
            rank.append(np.sum(img))
        idx_max = rank.index(max(rank))
        idx_min = rank.index(min(rank))
        bg = cv2.imread(MP_pth[idx_max], -1).astype(np.float64)
        bk = cv2.imread(MP_pth[idx_min], -1).astype(np.float64)
        bg = bg - bk
        if idx_max == idx_min + 1 or idx_max == 0:
            os.remove(MP_pth[idx_max])
            os.remove(MP_pth[idx_min])

            k = 0
            for i in range(idx_max + 1, len(MP_pth)):
                img = cv2.imread(MP_pth[i], -1).astype(np.float64)
                os.remove(MP_pth[i])
                img = img - bk
                bg[bg == 0] = 1
                img = (img / bg) * 255
                cv2.imwrite(sys.path[0] + '\\Masks_photo\\mask_{}.bmp'.format(k), img)
                k += 1
            for i in range(0, idx_min):
                img = cv2.imread(MP_pth[i], -1).astype(np.float64)
                os.remove(MP_pth[i])
                img = img - bk
                bg[bg == 0] = 1
                img = (img / bg) * 255
                cv2.imwrite(sys.path[0] + '\\Masks_photo\\mask_{}.bmp'.format(k), img)
                k += 1
            self.modelcontroller.gen_masks_phi_phi_s()

    def start_dmd(self):
        # 设置参数
        # 70 70 70 70 F5 F5 F5 F5 + 4字节的二值图延迟参数 (单位5ns) + 1字节的反极性 + 1字节的灰度等级
        # + 2字节的多少图片输出一个触发信号 + 2字节的触发延迟
        loop_num = int(self.dmdframe.text_loop_num.get(1.0, tk.END).rstrip('\n').strip())  # 默认播放张数为1张以使得循环结束
        loop_fre = int(float(self.dmdframe.text_loop_fre.get(1.0, tk.END).rstrip('\n')))  # 默认播放张数为1张/s
        begin_loc = int(self.dmdframe.text_begin_loc.get(1.0, tk.END))
        time_interval = int(200000000 / loop_fre)  # 5ns int
        print('loop_num: ', loop_num)
        print('loop_fre: ', loop_fre)
        print('begin_loc: ', begin_loc)
        print('time_interval: ', time_interval)
        time3 = time_interval & 255
        time2 = (time_interval >> 8) & 255
        time1 = (time_interval >> 16) & 255
        time0 = (time_interval >> 24) & 255

        # 加入帧头 控制判别信息
        Set_parameter_data = [0] * 19
        Set_parameter_data[0:8] = [112, 112, 112, 112, 245, 245, 245, 245]  # 70   F5
        # 加入4字节延时  频率1秒 200000000/256/256/256 =11     15450624/256/256=235
        # 49664/256=194
        Set_parameter_data[8:12] = [time0, time1, time2, time3]  # 10   F5
        # Set_parameter_data[8:12] = [11,235,194,0]
        Set_parameter_data[12:19] = [0, 0, 0,
                                     int(self.dmdframe.text_trigger_fre.get(1.0, tk.END).rstrip('\n').strip()) - 1, 0,
                                     0,
                                     0]  # 1字节的反极性 +  1字节的灰度等级
        # + 2字节的多少图片输出一个触发信号 + 2字节的触发延迟
        # 发送数据
        self.s.sendto(bytes(Set_parameter_data), self.addr_ser)
        time.sleep(0.5)

        # 0x30,0x30,0x30,0x30,0xF5,0xF5,0xF5,0xF5,
        # +8字节DDR起始播放地址 + 4字节图片播放张数
        Set_img_play_parameter = [0] * 20
        # 加入帧头
        Set_img_play_parameter[0:8] = [48, 48, 48, 48, 245, 245, 245, 245]  # 30   F5
        # 设置起始地址
        add_dat = int(self.Image_data_length * (begin_loc - 1) / self.DDR_NUM / 8)  # kai为想要图片开始的index
        add_4 = add_dat & 255
        add_3 = (add_dat >> 8) & 255
        add_2 = (add_dat >> 16) & 255
        add_1 = (add_dat >> 24) & 255
        Set_img_play_parameter[8:16] = [0, 0, 0, 0, add_1, add_2, add_3, add_4]  #
        # Set_img_play_parameter[8:16] = [0,0,0,0,0,0,0,0]
        # 播放张数
        Set_img_play_parameter[16:20] = [0, 0, 0, loop_num]  # 为何要四字节？
        # 发送数据
        self.s.sendto(bytes(Set_img_play_parameter), self.addr_ser)
        time.sleep(0.5)

    def pause_dmd(self):
        # 停止播放：
        # 0x60,0x60,0x60,0x60,0xF5,0xF5,0xF5,0xF5
        DMD_PAUSE_cmd = [0] * 8
        # 加入帧头
        DMD_PAUSE_cmd[0:8] = [96, 96, 96, 96, 245, 245, 245, 245]  # 60   FF
        # 发送数据
        self.s.sendto(bytes(DMD_PAUSE_cmd), self.addr_ser)
        # Add_Info('DMD播放暂停！')

    def stop_dmd(self):
        # 中止播放：
        # 0x90,0x90,0x90,0x90,0xF5,0xF5,0xF5,0xF5
        DMD_STOP_cmd = [0] * 8
        # 加入帧头
        DMD_STOP_cmd[0:8] = [144, 144, 144, 144, 245, 245, 245, 245]  # 90   FF
        # 发送数据
        self.s.sendto(bytes(DMD_STOP_cmd), self.addr_ser)
        # Add_Info('DMD终止播放！')

    def set_dmdframe(self, dmdframe):
        self.dmdframe = dmdframe
