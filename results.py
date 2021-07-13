#Construção da tabela de resultados

import numpy as np
import pandas as pd
import os
import imageio as io
from math import nan

import lsb_embed
import ebe_embed
import wavelet_embed
import metrics
import utils

a = sorted(os.listdir("cover_images/"))
payload = utils.read_payload("testdata/large.txt")
table = pd.DataFrame(columns=[
    'lsb_mse', 'lsb_psnr',
    'ebe_mse', 'ebe_psnr',
    'iwt_mse', 'iwt_psnr',
], index=a)


for filename in a:
    cover = np.asarray(io.imread("cover_images/" + filename, pilmode='RGB'))
    lsb = lsb_embed.Steg(cover.copy())
    ebe = ebe_embed.Steg(cover.copy())

    try:
        lsb_stego = lsb.embed(payload)
        lsb_mse = metrics.mse(cover, lsb_stego)
        lsb_psnr = metrics.psnr(cover, lsb_stego)
    except:
        lsb_mse = nan
        lsb_psnr = nan
    finally:
        table.at[filename, 'lsb_mse'] = lsb_mse
        table.at[filename, 'lsb_psnr'] = lsb_psnr

    try:
        ebe_stego = ebe.embed(payload)
        ebe_mse = metrics.mse(cover, ebe_stego)
        ebe_psnr = metrics.psnr(cover, ebe_stego)
    except:
        ebe_mse = nan
        ebe_psnr = nan
    finally:
        table.at[filename, 'ebe_mse'] = ebe_mse
        table.at[filename, 'ebe_psnr'] = ebe_psnr
    
    try:
        iwt_stego = wavelet_embed.embed(cover, payload)
        iwt_mse = metrics.mse(cover, iwt_stego)
        iwt_psnr = metrics.psnr(cover, iwt_stego)
    except:
        iwt_mse = nan
        iwt_psnr = nan
    finally:
        table.at[filename, 'iwt_mse'] = iwt_mse
        table.at[filename, 'iwt_psnr'] = iwt_psnr

table.to_csv("results.csv")