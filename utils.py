import matplotlib.pyplot as plt
import numpy as np

def read_as_bytes(path):
    data = []

    with open(path, 'rb') as f:
        while True:
            byte = f.read(1)
            if not byte:
                break
            else:
                data.append(byte)

    return data

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

