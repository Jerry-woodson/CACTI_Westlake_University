from torch import nn
import torch
from models.resdnet import ResDNetBlock
import einops


class Network(nn.Module):
    def __init__(self, in_ch=64, units=8, group_num=4):
        super().__init__()

        self.fem = nn.Sequential(
            nn.Conv3d(1, in_ch, kernel_size=(3, 7, 7), stride=1, padding=(1, 3, 3)),
            nn.LeakyReLU(inplace=True),
            nn.Conv3d(in_ch, in_ch * 2, kernel_size=3, stride=1, padding=1),
            nn.LeakyReLU(inplace=True),
            nn.Conv3d(in_ch * 2, in_ch * 4, kernel_size=3, stride=(1, 2, 2), padding=1),
            nn.LeakyReLU(inplace=True),
        )
        self.up_conv = nn.Conv3d(in_ch * 4, in_ch * 8, 1, 1)
        self.up = nn.PixelShuffle(2)
        self.vrm = nn.Sequential(
            nn.Conv3d(in_ch * 2, in_ch * 2, kernel_size=3, stride=1, padding=1),
            nn.LeakyReLU(inplace=True),
            nn.Conv3d(in_ch * 2, in_ch, kernel_size=1, stride=1),
            nn.LeakyReLU(inplace=True),
            nn.Conv3d(in_ch, 1, kernel_size=3, stride=1, padding=1),
        )
        self.resdnet_list = nn.ModuleList()
        for i in range(units):
            self.resdnet_list.append(ResDNetBlock(in_ch * 4, group_num=group_num))

    def forward(self, y, Phi, Phi_s):
        out_list = []
        print(y.size)
        print(Phi_s.size)
        meas_re = torch.div(y, Phi_s)
        meas_re = torch.unsqueeze(meas_re, 1)
        maskt = Phi.mul(meas_re)
        x = meas_re + maskt
        x = x.unsqueeze(1)

        out = self.fem(x)
        for resdnet in self.resdnet_list:
            out = resdnet(out)

        out = self.up_conv(out)
        out = einops.rearrange(out, "b c t h w-> b t c h w")
        out = self.up(out)
        out = einops.rearrange(out, "b t c h w-> b c t h w")
        out = self.vrm(out)

        out = out.squeeze(1)
        out_list.append(out)
        return out_list
