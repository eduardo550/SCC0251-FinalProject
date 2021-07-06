#Módulo para as métricas de avaliação de imagens usadas no trabalho

import numpy as np

def mse(cover, stego):
    assert cover.shape == stego.shape
    cover = cover.astype(np.double)
    stego = stego.astype(np.double)
    return np.mean(np.square(np.subtract(cover, stego)))

def psnr(cover, stego):
    mean_square_error = mse(cover, stego)
    cmax = np.amax(stego)

    aux = (cmax ** 2) / mean_square_error

    return 10 * np.log10(aux)
