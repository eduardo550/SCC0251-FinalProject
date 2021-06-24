# Nomes:    Eduardo de Sousa Siqueira       nUSP: 9278299
#           Igor Barbosa Grécia Lúcio       nUSP: 9778821
# SCC0251 - Image Processing          1 semestre 2021
# Partial Report

import numpy as np
import cv2
import types

#function to change the message to binary
def messageToBinary(message):
    if type(message) == str:
        return ''.join([ format(ord(i), "08b") for i in message ])
    elif type(message) == bytes or type(message) == np.ndarray:
        return [ format(i, "08b") for i in message ]
    elif type(message) == int or type(message) == np.uint8:
        return format(message, "08b")
    else:
        raise TypeError("Input type not supported")

#function to embed data into the message
def embed(image, data):
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8

    if len(data) > n_bytes:
        raise ValueError("Insufficient bytes, need bigger image or less data !!")

    data += "#####"
    data_index = 0
    binary_secret_msg = messageToBinary(data)
    data_len = len(binary_secret_msg)
    for values in image:
        for pixel in values:
            r, g, b = messageToBinary(pixel)
            if data_index < data_len:
                pixel[0] = int(r[:-1] + binary_secret_msg[data_index], 2)
                data_index += 1
            if data_index < data_len:
                pixel[1] = int(g[:-1] + binary_secret_msg[data_index], 2)
                data_index += 1
            if data_index < data_len:
                pixel[2] = int(b[:-1] + binary_secret_msg[data_index], 2)
                data_index += 1
            if data_index >= data_len:
                break
    return image

#function to show the hidden data
def showData(image):
    binary_data = ""
    for values in image:
        for pixel in values:
            r, g, b = messageToBinary(pixel)
            binary_data += r[-1]
            binary_data += g[-1]
            binary_data += b[-1]
    all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "#####":
            break
    return decoded_data[:-5]

def encode_text(image,data):
    filename = input("Enter new image name(without extension): ")
    encoded_image = embed(image, data)
    file = filename + ".png"
    cv2.imwrite(file, encoded_image)

def decode_text(image):
    text = showData(image)
    return text

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
    test_img = cv2.imread("cover_images/00001.jpg")

    a = input("Image Steganography\n 1. Encode\n 2. Decode\n Your input is: ")
    userinput = int(a)
    if (userinput == 1):
        print("\nEncoding...")
        testdata = ""
        with open("testdata/small.txt", 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                testdata += line
        encode_text(test_img,testdata)
    elif (userinput == 2):
        print("\nDecoding...")
        filename = input("Enter image name: ")
        img = cv2.imread(filename)
        print("Decoded message is " + decode_text(img))
        print("PSNR")
        print(psnr(test_img,img))
    return

if __name__ == "__main__":
    main()