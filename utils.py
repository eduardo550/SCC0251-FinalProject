import matplotlib.pyplot as plt
import numpy as np

#A partir de path, lê o arquivo e salva como bytes precedido por um header de 8 bytes com seu tamanho
def read_payload(path):
    with open(path, 'rb') as f:
        file = f.read()

    data = len(file).to_bytes(length=8, byteorder='big')

    return data + file

def plot_cover_stego(cover, stego):
    fig = plt.figure()
    fig.add_subplot(1, 2, 1)
    plt.imshow(cover)
    plt.title("Cover")
    fig.add_subplot(1, 2, 2)
    plt.imshow(stego)
    plt.title("Stego")
    plt.show()

def normalize(image, values):
    new_image = np.empty(shape=image.shape, dtype=image.dtype)
    new_max, new_min = values                               #intervalo dos novos valores
    old_max, old_min = (np.amax(image), np.amin(image))     #intervalo dos valores originais

    new_image = np.round(((image - old_min) * (new_max-new_min))/(old_max-old_min) + new_min, 4)
            
    return new_image

