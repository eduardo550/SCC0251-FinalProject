#Módulo que implementa esteganografia no domínio da frequência
#O algoritmo inclui o dado secreto nos bits menos significativos dos coeficientes da dct
#Defunct
import imageio as io
import sys
import numpy as np
from scipy.fft import dct, idct

import utils
import metrics

def dct2d(mat):
    return dct(dct(mat.T, norm='ortho').T, norm='ortho')

def idct2d(mat):
    return idct(idct(mat.T, norm='ortho').T, norm='ortho')

def rgb_dct(image):
    r_coefs = np.around(dct2d(image[:, :, 0])).astype(np.int32)
    g_coefs = np.around(dct2d(image[:, :, 1])).astype(np.int32)
    b_coefs = np.around(dct2d(image[:, :, 2])).astype(np.int32)

    return (r_coefs, g_coefs, b_coefs)

def idct_rgb(R, G, B):
    r = np.around(idct2d(R)).astype(np.uint8)
    g = np.around(idct2d(G)).astype(np.uint8)
    b = np.around(idct2d(B)).astype(np.uint8)

    return np.stack((r, g, b), axis=-1)

def valid_points(a):
    valids =  np.logical_and(
        a != 0,
        a != 1 
    )
    valids[0, 0] = False # O primeiro ponto não é manipulado
    return valids

def max_capacity(cover):
    r, g, b = rgb_dct(cover)

    r_capacity = (r[valid_points(r)].size) // 8
    g_capacity = (g[valid_points(g)].size) // 8
    b_capacity = (b[valid_points(b)].size) // 8

    return r_capacity + g_capacity + b_capacity

def embed(cover, payload):
    r, g, b = rgb_dct(cover)
    null_lsb_32 = np.invert(np.array(1, dtype=np.int32))    #np.int32 é o tipo escolhido para os coeficientes DCT
    bitmask_8bit = np.array(128, dtype=np.uint8)  #0b10000000

    for channel in [r.view(), g.view(), b.view()]:
        valid_rows, valid_cols = np.where(valid_points(channel))
        coords = list(zip(valid_rows, valid_cols))
        bytes_processed = 0
        bit_offset = 7
        cur_bitmask_8bit = bitmask_8bit.copy()

        for i, j in coords:
            #Navegação bit-a-bit
            cur_byte = payload[bytes_processed]
            cur_bit = (cur_byte & cur_bitmask_8bit) >> bit_offset

            channel[i, j] = channel[i, j] & null_lsb_32     #Nulificando último bit da imagem
            channel[i, j] = channel[i, j] | cur_bit
            
            bit_offset -= 1
            if(bit_offset < 0):
                bytes_processed += 1
                if(bytes_processed == len(payload)): break
                bit_offset = 7
                cur_bitmask_8bit = bitmask_8bit.copy()
            else:
                cur_bitmask_8bit = cur_bitmask_8bit >> 1    
        if(bytes_processed == len(payload)): break

    return r, g, b

def extract(r, g, b):
    #Extraindo 8 bytes do Header
    lsb_mask = np.array(1, r.dtype)
    valid_rows, valid_cols = np.where(valid_points(r))
    header_coords = list(zip(valid_rows, valid_cols))[:64]
    header = 0
    for i, j in header_coords:
        bit = r[i, j] & lsb_mask
        header = header | bit
        header = header << 1

    print(header)

def main(img_path, opt):

    if(opt == 'encode'):
        cover = np.asarray(io.imread(img_path))
        payload_path = "testdata/small.txt" #input("Payload filename: ").rstrip()
        payload = utils.read_payload(payload_path)
        m = max_capacity(cover)
        if (len(payload) > m):
            print(f"Payload of {len(payload)} bytes too big for cover image. Max payload capacity for this image: {m} bytes")
            return
        stego_r, stego_g, stego_b = embed(cover, payload)
        stego = idct_rgb(stego_r, stego_g, stego_b)
        stego_path = input("Stego image name(without extension): ").strip()
        stego_path = stego_path + '.png'
        io.imwrite(stego_path, stego, format='PNG-PIL', compress_level=0)
    elif(opt == 'decode'):
        stego = np.asarray(io.imread(img_path))
        print(stego[0, 1:65, 0])
        payload = extract(stego)
        print(f"Payload found: {payload}")
    else:
        print("Option not recognized.")

    return

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} [mode] [image_path]")
        print("Modes: encode decode")
        print("image_path is the name of the cover image for 'encode' or the name of the file containing the coeficients for 'decode'")
        sys.exit(0)
        
    user_opt = sys.argv[1]
    img_filename = sys.argv[2]
    main(img_filename, user_opt)