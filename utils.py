import ctypes
import inspect

import torch
import scipy.io as scio
import numpy as np
import logging
import time
import os
import os.path as osp
import cv2
from PIL import Image, ImageDraw, ImageFont


def save_image(out, gt, image_name, show_flag=False):
    sing_out = out.transpose(1, 0, 2).reshape(out.shape[1], -1)
    if gt is None:
        result_img = sing_out * 255
    else:
        sing_gt = gt.transpose(1, 0, 2).reshape(gt.shape[1], -1)
        result_img = np.concatenate([sing_out, sing_gt], axis=0) * 255
    result_img = result_img.astype(np.float32)
    cv2.imwrite(image_name, result_img)
    if show_flag:
        cv2.namedWindow("image", 0)
        cv2.imshow("image", result_img.astype(np.uint8))
        cv2.waitKey(0)


def get_images(image_temp):
    image_dict = {}
    for image_t in image_temp:
        image = Image.open(image_t.name)
        image = np.asarray(image).astype(np.float32)
        image /= image.max()
        k = image_t.orig_name.split(".")[0]
        if "_" in k:
            k = k.split("_")[-1]
        image_dict[k] = image
    image_dict = dict(sorted(image_dict.items(), key=lambda x: int(x[0])))
    image_value = list(image_dict.values())
    image_arr = np.array(image_value)
    return image_arr


def image_to_masks(mask_dir):
    mask_list = []
    mask_name_list = os.listdir(mask_dir)
    mask_name_list.sort(key=lambda x: int(x[5:-4]))
    for mask_name in mask_name_list:
        mask_path = osp.join(mask_dir, mask_name)
        mask = Image.open(mask_path)
        mask = np.asarray(mask).astype(np.float32)
        mask_list.append(mask)
    mask_array = np.array(mask_list)
    return mask_array


def mat_to_image(mask_path):
    if mask_path[-4:] == ".mat":
        mask_dict = scio.loadmat(mask_path)
        mask = mask_dict["meas"]
        if len(mask.shape) == 2:
            mask = np.expand_dims(mask, axis=2)
        mask = mask.transpose(2, 0, 1)
        for i in range(mask.shape[0]):
            cv2.imwrite("meas/{}.png".format(i), mask[i])
    return mask


def generate_masks(mask_path):
    if mask_path[-4:] == ".mat":
        mask_dict = scio.loadmat(mask_path)
        mask = mask_dict["mask"]
        if len(mask.shape) == 2:
            mask = np.expand_dims(mask, axis=2)
        d1, d2, d3 = mask.shape
        if d1 > d3:
            mask = mask.transpose(2, 0, 1)
    else:
        mask = image_to_masks(mask_path)
    if mask.max() > 10:
        mask /= mask.max()
    return mask


def A(x, Phi):
    temp = x * Phi
    y = torch.sum(temp, 1)
    return y


def At(y, Phi):
    temp = torch.unsqueeze(y, 1).repeat(1, Phi.shape[1], 1, 1)
    x = temp * Phi
    return x


def Logger(log_dir):
    if not osp.exists(log_dir):
        os.makedirs(log_dir)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(filename)s [line: %(lineno)s] - %(message)s")

    localtime = time.strftime("%Y_%m_%d_%H_%M_%S")
    logfile = osp.join(log_dir, localtime + ".log")
    fh = logging.FileHandler(logfile, mode="w")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def cv2ImgAddText(img, text, textColor, font_size, w):
    if (isinstance(img, np.ndarray)):
        img = Image.fromarray(img)
    draw = ImageDraw.Draw(img)
    fontStyle = ImageFont.truetype(
        "font/times.ttf", font_size)
    draw.text((w, 10), text, textColor, font=fontStyle)
    return np.asarray(img)


def rotate_image(image, rotate, index):
    image_shape = image.shape
    if len(image_shape) == 2:
        h, w = image_shape
    else:
        h, w, c = image_shape
    rot_mat = cv2.getRotationMatrix2D((w // 2, h // 2), -rotate, 1)
    image = cv2.warpAffine(image, rot_mat, (w, h))
    image = image * 255.
    image = image.astype(np.uint8)
    # image = cv2.putText(image,,(10,10),cv2.FONT_HERSHEY_COMPLEX,3,255)
    image = cv2ImgAddText(image, "#: {}".format(index + 1), (255), 50, w - 140)
    return image


def image2video(images, name="res", fps=4):
    video_path = "video_res/{}.mp4".format(name)
    f = len(images)
    h, w = images[0].shape
    size = (w, h)
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    # fourcc  = cv2.VideoWriter_fourcc('I', '4', '2', '0')
    video = cv2.VideoWriter(video_path, fourcc, fps, size, False)

    for idx in range(f):
        video.write(images[idx])
    video.release()
    cv2.destroyAllWindows()
    return video_path


def save_img(images):
    for i in range(len(images)):
        file_name = 'results/result_{}.png'.format(i)
        cv2.imwrite(file_name, images[i])


# 将返回的错误码转换为十六进制显示
def ToHexStr(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2 ** 32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr
    return hexStr


def del_files(dir_path):
    if os.path.isfile(dir_path):
        try:
            os.remove(dir_path)  # 这个可以删除单个文件，不能删除文件夹
        except BaseException as e:
            print(e)
    elif os.path.isdir(dir_path):
        file_lis = os.listdir(dir_path)
        for file_name in file_lis:
            tf = os.path.join(dir_path, file_name)
            del_files(tf)
    print('ok')


# 获取选取设备信息的索引，通过[]之间的字符去解析
def TxtWrapBy(start_str, end, all):
    start = all.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = all.find(end, start)
        if end >= 0:
            return all[start:end].strip()


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
