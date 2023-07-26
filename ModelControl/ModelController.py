import os
import time
import tkinter.messagebox
from customtkinter import CTkImage
import numpy as np
from PIL import Image, ImageTk
from einops import einops
from torch.cuda.amp import autocast
import tkinter as tk

from models.network import Network
import torch

from utils import generate_masks, rotate_image, save_img, stop_thread


class ModelController:
    def __init__(self, meas_dir, measurementframe=None, master=None):
        self.network = None
        self.mask = None
        self.Phi = None
        self.Phi_s = None
        self.mask_dir = 'Masks_photo'
        self.device = 'cuda'
        self.measurementframe = measurementframe
        self.meas_dir = meas_dir
        self.meas_idx = 1
        self.master = master

    def init_model(self):
        device = "cuda"
        network = Network()
        network = network.to(device)
        network.load_state_dict(torch.load("checkpoints/EfficientSCI_last_real.pth"))
        network = network.eval()
        self.network = network

    def gen_masks_phi_phi_s(self):
        if len(os.listdir(self.mask_dir)) != 0:
            self.mask = generate_masks(self.mask_dir)
            self.mask = self.mask[0:10]
            mask_s = np.sum(self.mask, axis=0)
            mask_s[mask_s == 0] = 1
            self.Phi = einops.repeat(self.mask, 'cr h w->b cr h w', b=1)
            self.Phi_s = einops.repeat(mask_s, 'h w->b h w', b=1)
            self.Phi = torch.from_numpy(self.Phi).to(self.device)
            self.Phi_s = torch.from_numpy(self.Phi_s).to(self.device)

    def test(self, rotate_value=0):
        if len(os.listdir(self.mask_dir)):
            self.gen_masks_phi_phi_s()
            start = time.time()
            meas_path = os.path.join(self.meas_dir, "meas_{}.bmp".format(self.meas_idx))
            print('reconstructing measurement No.{}'.format(self.meas_idx))
            try:
                meas = Image.open(meas_path)
                meas_display = meas.resize((325, 325))
                meas_display = rotate_image(np.array(meas_display) / 255., rotate_value, self.meas_idx)
                meas_display = Image.fromarray(meas_display)
                meas_display = CTkImage(meas_display, size=(325, 325))
                self.measurementframe.meas_panel.configure(image=meas_display)
                self.measurementframe.meas_panel.image = meas_display
                meas = np.asarray(meas)
                meas = meas.astype(np.float32) / 255 * self.mask.shape[0] / 2
                meas = torch.from_numpy(meas).to(self.device)
                meas = meas.unsqueeze(0)
                with torch.no_grad():
                    torch.cuda.synchronize()
                    with autocast():
                        outputs = self.network(meas, self.Phi, self.Phi_s)
                    torch.cuda.synchronize()
                    out = outputs[-1][0].cpu().numpy().astype(np.float32)
                    out = out / np.max(out)
                    out = out.clip(0, 1)
                res_list = []
                for i in range(out.shape[0]):
                    out_r = rotate_image(out[i], rotate_value, i)
                    res_list.append(out_r)
                save_img(res_list)
                self.meas_idx += 1
                print('reconstruction finished in: {} secs'.format(time.time() - start))
            except FileNotFoundError:
                tkinter.messagebox.showerror(message="找不到文件")
                self.master.reconstructionframe.stop_recon()

    def set_meas_idx(self, meas_idx):
        self.meas_idx = meas_idx
