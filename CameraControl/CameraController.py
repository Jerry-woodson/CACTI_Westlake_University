import time
import constant
from CamOperation_class import *
from utils import ToHexStr, stop_thread
import tkinter


def TxtWrapBy(start_str, end, all_device):
    start = all_device.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = all_device.find(end, start)
        if end >= 0:
            return all_device[start:end].strip()


class CameraController:
    def __init__(self, streamframe=None, cameraframe=None, master=None):
        self.height = None
        self.width = None
        self.offsety = None
        self.offsetx = None
        self.gain = None
        self.exposure_time = None
        self.frame_rate = None
        self.devList = None
        self.devicelist = MV_CC_DEVICE_INFO_LIST()
        self.tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
        self.cam = MvCamera()
        self.nSelCamIndex = 0
        self.obj_cam_operation = 0
        self.b_is_run = False
        self.streamframe = streamframe
        self.cameraframe = cameraframe
        self.master = master
        self.auto_adjust_exposure_time_thread = None

    def enum_devices(self):
        self.devicelist = MV_CC_DEVICE_INFO_LIST()
        tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
        ret = MvCamera.MV_CC_EnumDevices(tlayerType, self.devicelist)
        if ret != 0:
            tkinter.messagebox.showerror('show error', 'enum devices fail! ret = ' + ToHexStr(ret))

        if self.devicelist.nDeviceNum == 0:
            tkinter.messagebox.showinfo('show info', 'find no device!')

        print("Find %d devices!" % self.devicelist.nDeviceNum)

        self.devList = []
        for i in range(0, self.devicelist.nDeviceNum):
            mvcc_dev_info = cast(self.devicelist.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                print("\ngige device: [%d]" % i)
                chUserDefinedName = ""
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName:
                    if 0 == per:
                        break
                    chUserDefinedName = chUserDefinedName + chr(per)
                print("device model name: %s" % chUserDefinedName)

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
                self.devList.append(
                    "[" + str(i) + "]GigE: " + chUserDefinedName + "(" + str(nip1) + "." + str(nip2) + "." + str(
                        nip3) + "." + str(nip4) + ")")
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print("\nu3v device: [%d]" % i)
                chUserDefinedName = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName:
                    if per == 0:
                        break
                    chUserDefinedName = chUserDefinedName + chr(per)
                print("device model name: %s" % chUserDefinedName)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("user serial number: %s" % strSerialNumber)
                self.devList.append("[" + str(i) + "]USB: " + chUserDefinedName + "(" + str(strSerialNumber) + ")")
            # return self.devList
            self.cameraframe.device_list["value"] = self.devList
            self.cameraframe.device_list.configure(values=self.devList)

    def xFunc(self, device_list):
        self.nSelCamIndex = TxtWrapBy("[", "]", device_list.get())

    def open_device(self):
        if self.b_is_run:
            tkinter.messagebox.showinfo('show info', 'Camera is Running!')
            return
        self.obj_cam_operation = CameraOperation(self.cam, self.devicelist, self.nSelCamIndex)
        ret = self.obj_cam_operation.Open_device()
        if 0 != ret:
            self.b_is_run = False
        else:
            self.master.model_val.set('continuous')
            self.b_is_run = True

    # ch:开始取流 | en:Start grab image
    def start_grabbing(self):
        self.obj_cam_operation.Start_grabbing(self.streamframe, self.streamframe.image_panel)

    # ch:停止取流 | en:Stop grab image
    def stop_grabbing(self):
        self.obj_cam_operation.Stop_grabbing()

        # ch:关闭设备 | Close device

    def close_device(self):
        self.obj_cam_operation.Close_device()
        self.b_is_run = False

    # ch:设置触发模式 | en:set trigger mode
    def set_triggermode(self):
        strMode = self.cameraframe.master.model_val.get()
        self.obj_cam_operation.Set_trigger_mode(strMode)

    # ch:设置触发命令 | en:set trigger software
    def trigger_once(self, triggercheck_val):
        nCommand = triggercheck_val.get()
        self.obj_cam_operation.Trigger_once(nCommand)

    # ch:保存bmp图片 | en:save bmp image
    def bmp_save(self):
        self.obj_cam_operation.b_save_bmp = True

    def bmp_save_mask(self):
        self.obj_cam_operation.b_save_bmp_mask = True

    # ch:保存jpg图片 | en:save jpg image
    def jpg_save(self):
        self.obj_cam_operation.b_save_jpg = True

    # 获取相机的各项参数
    def get_parameter(self):
        # 获取相机参数
        self.obj_cam_operation.Get_parameter()
        self.frame_rate = self.obj_cam_operation.frame_rate
        self.exposure_time = self.obj_cam_operation.exposure_time
        self.gain = self.obj_cam_operation.gain
        self.offsetx = self.obj_cam_operation.offsetx
        self.offsety = self.obj_cam_operation.offsety
        self.width = self.obj_cam_operation.width
        self.height = self.obj_cam_operation.height

        # 删除原有的相机参数
        self.cameraframe.text_frame_rate.delete(1.0, tk.END)
        self.cameraframe.text_exposure_time.delete(1.0, tk.END)
        self.cameraframe.text_gain.delete(1.0, tk.END)
        self.cameraframe.text_offsetx.delete(1.0, tk.END)
        self.cameraframe.text_offsety.delete(1.0, tk.END)
        self.cameraframe.text_width.delete(1.0, tk.END)
        self.cameraframe.text_height.delete(1.0, tk.END)

        # 在文本框中插入获取到的相机参数
        self.cameraframe.text_frame_rate.insert(1.0, self.frame_rate)
        self.cameraframe.text_exposure_time.insert(1.0, int(self.exposure_time) + 425)
        self.cameraframe.text_gain.insert(1.0, self.gain)
        self.cameraframe.text_offsetx.insert(1.0, self.offsetx)
        self.cameraframe.text_offsety.insert(1.0, self.offsety)
        self.cameraframe.text_width.insert(1.0, self.width)
        self.cameraframe.text_height.insert(1.0, self.height)

    # 设置相机的各项参数
    def set_parameter(self):
        # 从文本框中获取相机参数
        self.frame_rate = float(self.cameraframe.text_frame_rate.get(1.0, tk.END))
        self.exposure_time = float(self.cameraframe.text_exposure_time.get(1.0, tk.END))
        self.gain = float(self.cameraframe.text_gain.get(1.0, tk.END))
        self.offsetx = float(self.cameraframe.text_offsetx.get(1.0, tk.END))
        self.offsety = float(self.cameraframe.text_offsety.get(1.0, tk.END))
        self.width = float(self.cameraframe.text_width.get(1.0, tk.END))
        self.height = float(self.cameraframe.text_height.get(1.0, tk.END))

        self.obj_cam_operation.exposure_time = str(
            int(float(self.exposure_time - 425)))
        self.obj_cam_operation.exposure_time = self.obj_cam_operation.exposure_time.rstrip("\n")
        self.obj_cam_operation.gain = str(self.gain)
        self.obj_cam_operation.gain = self.obj_cam_operation.gain.rstrip("\n")
        self.obj_cam_operation.frame_rate = str(self.frame_rate)
        self.obj_cam_operation.frame_rate = self.obj_cam_operation.frame_rate.rstrip("\n")
        self.obj_cam_operation.offsetx = float(str(self.offsetx).rstrip('\n').strip())
        self.obj_cam_operation.offsety = float(str(self.offsety).rstrip('\n').strip())
        self.obj_cam_operation.width = float(str(self.width).rstrip('\n').strip())
        self.obj_cam_operation.height = float(str(self.height).rstrip('\n').strip())
        self.obj_cam_operation.Set_parameter(self.obj_cam_operation.frame_rate, self.obj_cam_operation.exposure_time,
                                             self.obj_cam_operation.gain, self.cameraframe.text_max_value)
        self.get_parameter()

    # 恢复相机最大画幅
    def restore_roi(self):
        self.obj_cam_operation.width = constant.WIDTH
        self.obj_cam_operation.height = constant.HEIGHT
        self.obj_cam_operation.offsetx = constant.OFFSETX
        self.obj_cam_operation.offsety = constant.OFFSETY
        self.obj_cam_operation.Set_parameter(self.obj_cam_operation.frame_rate, self.obj_cam_operation.exposure_time,
                                             self.obj_cam_operation.gain, self.cameraframe.text_max_value)
        self.get_parameter()

    # 持续拍摄burst_num张照片
    def burst(self, burst_num):
        if self.obj_cam_operation.burst_num != -1:
            self.obj_cam_operation.burst_num = int(burst_num)

    # 持续拍摄
    def keep_burst(self):
        if self.master.dmdframe.text_compression_rate.get(1.0, tk.END) == '\n':
            tkinter.messagebox.showinfo("Info", "压缩比不能为空")
            return
        self.cameraframe.master.dmdcontroller.pause_dmd()
        self.cameraframe.master.dmdcontroller.stop_dmd()
        self.cameraframe.master.model_val.set('triggermode')
        self.set_triggermode()

        self.cameraframe.master.dmdframe.text_trigger_fre.delete(1.0, tk.END)
        self.cameraframe.master.dmdframe.text_trigger_fre.insert(1.0,
                                                                 str(len(self.cameraframe.master.dmdcontroller.imgDir)))

        self.obj_cam_operation.Get_parameter()
        self.cameraframe.master.dmdframe.text_loop_fre.delete(1.0, tk.END)
        self.cameraframe.master.dmdframe.text_loop_fre.insert(1.0, str(int(
            self.cameraframe.master.dmdframe.text_compression_rate.get(1.0, tk.END).rstrip('\n')) * int(float(
            self.cameraframe.text_frame_rate.get(1.0, tk.END).rstrip('\n')))))

        self.cameraframe.master.dmdframe.text_loop_num.delete(1.0, tk.END)
        self.cameraframe.master.dmdframe.text_loop_num.insert(1.0,
                                                              str(len(self.cameraframe.master.dmdcontroller.imgDir)))

        self.cameraframe.master.dmdframe.text_begin_loc.delete(1.0, tk.END)
        self.cameraframe.master.dmdframe.text_begin_loc.insert(1.0, '1')
        self.cameraframe.master.dmdcontroller.start_dmd()
        self.cameraframe.text_burst_num.delete(1.0, tk.END)
        self.obj_cam_operation.burst_num = -1

        return

    def stop_burst(self):
        self.cameraframe.master.dmdcontroller.pause_dmd()
        self.cameraframe.master.dmdcontroller.stop_dmd()
        if self.cameraframe.text_burst_num.get(1.0, tk.END).rstrip('\n').strip() == "":
            self.obj_cam_operation.burst_num = 0
        else:
            int(self.cameraframe.text_burst_num.get(1.0, tk.END).rstrip('\n').strip())
        all_files = os.listdir('./Measurement')
        all_files.sort(key=lambda x: int(x[5:-4]), reverse=True)
        os.remove(os.path.join(os.getcwd(), "Measurement", all_files[0]))
        os.remove(os.path.join(os.getcwd(), "Measurement", all_files[-1]))
        self.cameraframe.master.model_val.set('continuous')
        self.set_triggermode()

        return

    def auto_adjust_exposure_time(self):
        while True:
            max_value = self.cameraframe.text_max_value.get(1.0, tk.END)
            if max_value == '\n' or max_value == '':
                stop_thread(self.auto_adjust_exposure_time_thread)
                self.auto_adjust_exposure_time_thread = None
                break
            elif max_value != '' and max_value not in range(235, 245):
                print(self.exposure_time)
                print(max_value)
                self.get_parameter()
                if float(max_value) > 245:
                    self.exposure_time -= 925
                    self.cameraframe.text_exposure_time.delete(1.0, tk.END)
                    self.cameraframe.text_exposure_time.insert(1.0, self.exposure_time)
                if float(max_value) < 235:
                    self.exposure_time += 925
                    self.cameraframe.text_exposure_time.delete(1.0, tk.END)
                    self.cameraframe.text_exposure_time.insert(1.0, self.exposure_time)
                self.set_parameter()
                time.sleep(0.1)
        self.frame_rate = 1000000 / (self.exposure_time + 425)
        self.cameraframe.text_frame_rate.delete(1.0, tk.END)
        self.cameraframe.text_frame_rate.insert(1.0, self.frame_rate)
        tkinter.messagebox.showinfo("Info", "自动调曝光完成")

    def auto_adjust_exposure_time_threading(self):
        self.auto_adjust_exposure_time_thread = threading.Thread(target=self.auto_adjust_exposure_time)
        self.auto_adjust_exposure_time_thread.start()

    def set_streamframe(self, streamframe):
        self.streamframe = streamframe

    def set_cameraframe(self, cameraframe):
        self.cameraframe = cameraframe
