#Módulo que implementa esteganografia com base em coeficientes da transformada do cosseno discreta
#O algoritmo inclui o dado secreto nos bits menos significativos dos coeficientes da transformada
#É implementado pela ferramenta JSteg, uma das mais famosas na área

import imageio as io
import sys
import numpy as np
from scipy.fftpack import dct, idct

import utils
import metrics

def embed(cover, payload):
    stego = dct(cover) #Stego image

    return utils.normalize(stego, (255, 0)).astype(cover.dtype)

def extract(stego):
    payload = []

    return payload

def main(img_path, opt, payload_path):

    if(opt == 'encode'):
        cover = np.asarray(io.imread(img_path))
        payload = utils.read_as_bytes(payload_path)
        stego = embed(cover, payload)
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