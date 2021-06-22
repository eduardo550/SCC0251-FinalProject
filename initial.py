import numpy as np
import imageio as io

def embed(image, data):
    #TODO
    return image

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

def main():
    test_img = io.imread("cover_images/00001.jpg")
    testdata = bytearray('', 'UTF-8')
    with open("testdata/small.txt", 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            testdata.extend(line.encode('UTF-8'))

    #TODO: fazer o embed, printar as imgs com matplotlib e os erros
    
    return

if __name__ == "__main__":
    main()