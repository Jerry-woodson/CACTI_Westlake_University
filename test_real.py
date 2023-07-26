import os
import torch
import os.path as osp
import numpy as np
import einops
import time
from PIL import Image
from torch.cuda.amp import autocast
from models.network import Network
from utils import rotate_image, image2video, generate_masks

os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def init_model():
    device = "cuda"
    network = Network()
    network = network.to(device)
    network.load_state_dict(torch.load("checkpoints/EfficientSCI_last_real.pth"))
    network = network.eval()
    return network


network = init_model()


def test(meas_dir, mask_path, cr=10, rotate_value=0):
    start = time.time()
    device = "cuda"
    mask = generate_masks(mask_path)
    mask = mask[0:cr]
    mask_s = np.sum(mask, axis=0)
    mask_s[mask_s == 0] = 1
    Phi = einops.repeat(mask, 'cr h w->b cr h w', b=1)
    Phi_s = einops.repeat(mask_s, 'h w->b h w', b=1)
    Phi = torch.from_numpy(Phi).to(device)
    Phi_s = torch.from_numpy(Phi_s).to(device)

    for meas_name in os.listdir(meas_dir):
        meas_path = osp.join(meas_dir, meas_name)
        meas = Image.open(meas_path)
        meas = np.asarray(meas)
        meas = meas.astype(np.float32) / 255 * mask.shape[0] / 2
        meas = torch.from_numpy(meas).to(device)
        meas = meas.unsqueeze(0)
        with torch.no_grad():
            torch.cuda.synchronize()

            with autocast():
                outputs = network(meas, Phi, Phi_s)
            torch.cuda.synchronize()

            out = outputs[-1][0].cpu().numpy().astype(np.float32)
            out = out.clip(0, 1)
        res_list = []
        for i in range(out.shape[0]):
            out_r = rotate_image(out[i], rotate_value, i)
            res_list.append(out_r)
        _name = meas_name.split(".")[0]
        image2video(res_list, _name)
        end = time.time()
        print("run time: {}".format(end - start))


if __name__ == "__main__":
    meas_dir = "test_meas"
    mask_path = "test_masks"

    test(meas_dir, mask_path, cr=10, rotate_value=0)
