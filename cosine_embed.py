#Módulo que implementa esteganografia com base em coeficientes da transformada do cosseno discreto

import sys

def embed(cover, payload):
    stego = [] #Stego image

    return stego

def extract(stego):
    payload = []

    return payload

def main(img_path, opt, payload):


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