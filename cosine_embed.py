#Módulo que implementa esteganografia no domínio da frequência
#O algoritmo inclui o dado secreto nos bits menos significativos dos coeficientes da dct

import imageio as io
import sys
import numpy as np
from scipy.fft import dct
from numpy.lib import stride_tricks

import utils
import metrics

def _cosine_rgb_transform(image):
    r = dct(image[:,:,0], type=2, norm='ortho')
    g = dct(image[:,:,1], type=2, norm='ortho')
    b = dct(image[:,:,2], type=2, norm='ortho')

    return (r, g, b)

def _cosine_rgb_reverse(r, g, b):
    ir = dct(r, type=3, norm='ortho')
    ig = dct(g, type=3, norm='ortho')
    ib = dct(b, type=3, norm='ortho')

    return np.stack((ir, ig, ib), axis=-1)

def _valid_pixels(mat):
    return np.logical_and(mat != 0, np.logical_and(mat != 1, mat != -1))

def max_capacity(cover):
    r, g, b = _cosine_rgb_transform(cover)
    rcap = r[_valid_pixels(r)].size
    gcap = g[_valid_pixels(g)].size
    bcap = b[_valid_pixels(b)].size

    return (rcap + gcap + bcap) // 8


def embed(cover, payload):
    pass


    #return _cosine_rgb_reverse(r, g, b).astype(cover.dtype)

def extract(stego):
    pass

def main(img_path, opt, payload_path):

    if(opt == 'encode'):
        cover = np.asarray(io.imread(img_path))
        payload = utils.read_payload(payload_path)
        m = max_capacity(cover)
        if (len(payload) > m):
            print(f"Payload of {len(payload)} bytes too big for cover image. Max payload capacity for this image: {m} bytes")
            return
        stego = embed(cover, payload)
        #utils.plot_cover_stego(cover, stego)
        #stego_path = input("Stego image name(without extension): ").strip()
        #stego_path = stego_path + '.png'
        #io.imwrite(stego_path, stego)
    else:
        print("Option not recognized.")

    return

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} [mode] [image_path] [payload_path]")
        print("Modes: encode decode")
        print("image_path is the name of the cover image for 'encode' or the name of the stego object for 'decode'")
        print("payload_path refers to the data to embed in image for 'encode' or the name of a file to save the extracted data for 'decode'")
        sys.exit(0)
        
    user_opt = sys.argv[1]
    img_filename = sys.argv[2]
    payload_name = sys.argv[3]
    main(img_filename, user_opt, payload_name)