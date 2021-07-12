# Módulo que implementa esteganografia no domínio da frequência
# Algoritmo definido em: P. W. Adi, F. Z. Rahmanti and N. A. Abu, 
# "High quality image steganography on integer Haar Wavelet Transform using modulus function," 
# 2015 International Conference on Science in Information Technology (ICSITech), 2015, pp. 79-84, doi: 10.1109/ICSITech.2015.7407781.

import imageio as io
import sys
import numpy as np

import utils
import metrics

#Integer Haar Wavelet Transform
###Implementation found in https://stackoverflow.com/a/15868889
def _iwt(array):
    output = np.zeros_like(array)
    nx, ny = array.shape
    x = nx // 2
    for j in range(ny):
        output[0:x,j] = (array[0::2,j] + array[1::2,j])//2
        output[x:nx,j] = array[0::2,j] - array[1::2,j]
    return output

def _iiwt(array):
    output = np.zeros_like(array)
    nx, ny = array.shape
    x = nx // 2
    for j in range(ny):
        output[0::2,j] = array[0:x,j] + (array[x:nx,j] + 1)//2
        output[1::2,j] = output[0::2,j] - array[x:nx,j]
    return output

def iwt2(array):
    return _iwt(_iwt(array.astype(int)).T).T

def iiwt2(array):
    return _iiwt(_iiwt(array.astype(int).T).T)
###

def get_bands(mat):
    rows, cols = mat.shape[0] // 2, mat.shape[1] //2
    cA = mat[0:rows, 0:cols]
    cH = mat[0:rows, cols:]
    cV = mat[rows:, 0:cols]
    cD = mat[rows:, cols:]

    return cA, cH, cV, cD

def reconstruct_mat(cA, cH, cV, cD):
    rows, cols = cA.shape
    s = rows*2, cols*2#Shape
    new_image = np.zeros(s)

    new_image[0:rows, 0:cols] = cA
    new_image[0:rows, cols:] = cH
    new_image[rows:, 0:cols] = cV
    new_image[rows:, cols:] = cD

    return new_image

def max_capacity(cover, threshold=2):
    _, a, b, c = get_bands(iwt2(cover))
    cap = a.size + b.size + c.size
    return (cap * threshold) // 8

def get_next_bits(byte_buffer, digits, amount):
    bitmask = 1
    for i in range(digits-1):
        bitmask = (bitmask << 1)+1

    bytes_processed = 0    
    bitarray = np.zeros(amount, int)
    bitarray_idx = 0
    for byte in byte_buffer:
        for offset in range(8-digits, -1, -digits):
            bitarray[bitarray_idx] = (byte & (bitmask << offset)) >> offset
            bitarray_idx += 1
        bytes_processed += 1
        if(bitarray_idx >= amount): break

    return bitarray, bytes_processed

def embed_values(coefs, rk, tk, bits):
    m = np.abs(rk - tk)
    mcomplement = (2**bits) - m
    g = np.empty(coefs[0].shape)
    gnext = np.copy(g)

    first_cond_indexing = rk > tk
    second_cond_indexing = m <= 2 ** bits
    third_cond_indexing = coefs[0] >= coefs[1]

    #O algoritmo modular envolve a aplicação de 8 regras com permutações das condições acima
    #Regra a) rk > tk and m <= 2^bits and gij >= gi,j+1
    a_idx = np.logical_and(first_cond_indexing, np.logical_and(second_cond_indexing, third_cond_indexing))
    g_old, g_old_next, m_ = coefs[0][a_idx], coefs[1][a_idx], m[a_idx]
    g[a_idx], gnext[a_idx] = (g_old - np.ceil(m_/2), g_old_next - np.floor(m_/2))
    #Regra b) rk > tk and m <= 2^bits and gij < gi,j+1
    b_idx = np.logical_and(first_cond_indexing, np.logical_and(second_cond_indexing, np.logical_not(third_cond_indexing)))
    g_old, g_old_next, m_ = coefs[0][b_idx], coefs[1][b_idx], m[b_idx]
    g[b_idx], gnext[b_idx] = (g_old - np.floor(m_/2), g_old_next - np.ceil(m_/2))
    #Regra c) rk > tk and m > 2^bits and gij >= gi,j+1
    c_idx = np.logical_and(first_cond_indexing, np.logical_and(np.logical_not(second_cond_indexing), third_cond_indexing))
    g_old, g_old_next, m_ = coefs[0][c_idx], coefs[1][c_idx], mcomplement[c_idx]
    g[c_idx], gnext[c_idx] = (g_old + np.floor(m_/2), g_old_next + np.ceil(m_/2))
    #Regra d) rk > tk and m > 2^bits and gij < gi,j+1
    d_idx = np.logical_and(first_cond_indexing, np.logical_and(np.logical_not(second_cond_indexing), np.logical_not(third_cond_indexing)))
    g_old, g_old_next, m_ = coefs[0][d_idx], coefs[1][d_idx], mcomplement[d_idx]
    g[d_idx], gnext[d_idx] = (g_old + np.ceil(m_/2), g_old_next + np.floor(m_/2))
    #Regra e) rk <= tk and m <= 2^bits and gij >= gi,j+1
    e_idx = np.logical_and(np.logical_not(first_cond_indexing), np.logical_and(second_cond_indexing, third_cond_indexing))
    g_old, g_old_next, m_ = coefs[0][e_idx], coefs[1][e_idx], m[e_idx]
    g[e_idx], gnext[e_idx] = (g_old + np.floor(m_/2), g_old_next + np.ceil(m_/2))
    #Regra f) rk <= tk and m <= 2^bits and gij < gi,j+1
    f_idx = np.logical_and(np.logical_not(first_cond_indexing), np.logical_and(second_cond_indexing, np.logical_not(third_cond_indexing)))
    g_old, g_old_next, m_ = coefs[0][f_idx], coefs[1][f_idx], m[f_idx]
    g[f_idx], gnext[f_idx] = (g_old + np.ceil(m_/2), g_old_next + np.floor(m_/2))
    #Regra g) rk <= tk and m > 2^bits and gij >= gi,j+1
    g_idx = np.logical_and(np.logical_not(first_cond_indexing), np.logical_and(np.logical_not(second_cond_indexing), third_cond_indexing))
    g_old, g_old_next, m_ = coefs[0][g_idx], coefs[1][g_idx], mcomplement[g_idx]
    g[g_idx], gnext[g_idx] = (g_old - np.ceil(m_/2), g_old_next - np.floor(m_/2))
    #Regra h) rk <= tk and m > 2^bits and gij < gi,j+1
    h_idx = np.logical_and(np.logical_not(first_cond_indexing), np.logical_and(np.logical_not(second_cond_indexing), np.logical_not(third_cond_indexing)))
    g_old, g_old_next, m_ = coefs[0][h_idx], coefs[1][h_idx], mcomplement[h_idx]
    g[h_idx], gnext[h_idx] = (g_old - np.floor(m_/2), g_old_next - np.ceil(m_/2))

    return g, gnext

def embed(cover, payload, threshold=2):
    WEIGHTING = 2   #constante determinada no artigo
    #Preprocessamento
    clipped_cover = np.clip(cover, threshold*WEIGHTING, 255 - (threshold*WEIGHTING))
    #Aplicação da transformada
    freq = iwt2(clipped_cover)
    cA, cH, cV, cD = get_bands(freq)    #cA não é alterada, pois causa a maior distorção na imagem

    bytes_processed = 0
    while(bytes_processed < len(payload)):
        for band in [cH.view(), cV.view(), cD.view()]:
            evens, odds = (band[:, ::2], band[:, 1::2])
            remainder_groups = (evens + odds) % (2 ** threshold)
            t_values, b = get_next_bits(payload[bytes_processed:], threshold, remainder_groups.size)
            bytes_processed += b
            t_values = t_values.reshape(remainder_groups.shape)
            band[:, ::2], band[:, 1::2] = embed_values((evens, odds), remainder_groups, t_values, threshold)
        #endfor
    #endwhile

    #Transformada inversa, construindo a imagem no domínio espacial
    stego = reconstruct_mat(cA, cH, cV, cD)
    return iiwt2(stego).astype(cover.dtype)

def extract(stego, threshold=2):
    #Convertendo para wavelets
    freq = iwt2(stego)
    _, *bands = get_bands(freq)

    evens, odds = (bands[0][:, ::2], bands[0][:, 1::2])
    remainder_groups = np.ravel((evens + odds) % (2 ** threshold))
    #Extraindo header: cada elemento de remainder_groups é threshold bits do payload original
    header_bits = (8*8) // threshold    #8 bytes * 8 bits por byte
    header = remainder_groups[:header_bits]
    payload_size = 0
    for digits in header:
        payload_size = payload_size << threshold
        payload_size += digits

    payload = 0
    cur = remainder_groups[header_bits:]
    band_idx = 0
    idx = 0
    for bit in range((payload_size*8)//threshold):
        payload = payload << threshold
        payload += cur[idx]
        idx += 1
        if(idx >= cur.size):
            band_idx += 1
            evens, odds = (bands[band_idx][:, ::2], bands[band_idx][:, 1::2])
            cur = np.ravel((evens + odds) % (2 ** threshold))
            idx = 0

def main(img_path, opt):
    np.set_printoptions(threshold=sys.maxsize)
    if(opt == 'encode'):
        cover = np.asarray(io.imread(img_path, pilmode='L'))
        payload_path = "testdata/small.txt" #input("Payload filename: ").rstrip()
        payload = utils.read_payload(payload_path)
        m = max_capacity(cover)
        if(m < len(payload)):
            print(f"Payload of {len(payload)} bytes cannot be embedded in this cover image. Max capacity: {m} bytes")
            return
        stego = embed(cover, payload)
        # print(np.array_equal(cover, stego))
        # utils.plot_cover_stego(cover, stego)
        #stego_path = input("Stego image name(without extension): ").strip()
        stego_path = 'bla' + '.png'
        io.imwrite(stego_path, stego, format='PNG-PIL', compress_level=0)
    elif(opt == 'decode'):
        stego = np.asarray(io.imread(img_path))
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