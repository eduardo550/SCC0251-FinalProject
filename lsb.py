#!/usr/bin/env python
# coding:UTF-8

import sys
import cv2
import numpy as np
import math

class SteganographyException(Exception):
    pass

class Steg():
    def __init__(self, im):
        self.image = im
        self.height, self.width, self.nbchannels = im.shape
        self.size = self.width * self.height
        
        self.maskONE = 1 #Will be used to do bitwise operations
        self.maskZERO = 254
        
        self.curwidth = 0  # Current width position
        self.curheight = 0 # Current height position
        self.curchan = 0   # Current channel position
        
    def next_slot(self): #Move to the next slot were information can be taken or put
        if self.curchan == self.nbchannels-1:
            self.curchan = 0 #Next Space is the first channel of the next pixel
            if self.curwidth == self.width-1:
                self.curwidth = 0 #Next Space is the first pixel
                self.curheight +=1 #of the following line
            else:
                self.curwidth +=1 #Next Space is the following pixel of the same line
        else:
            self.curchan +=1 #Next Space is the following channel

    def put_binary_value(self, bits): #Put the bits in the image
        for c in bits:
            val = list(self.image[self.curheight,self.curwidth]) #Get the pixel value as a list
            if int(c) == 1:
                val[self.curchan] = int(val[self.curchan]) | self.maskONE #OR with maskONE
            else:
                val[self.curchan] = int(val[self.curchan]) & self.maskZERO #AND with maskZERO
                
            self.image[self.curheight,self.curwidth] = tuple(val)
            self.next_slot() #Move "cursor" to the next space
        return

    def lsb_max_capacity(self):
        return (self.size*self.nbchannels)/8

    def read_bit(self): #Read a single bit into the image
        val = self.image[self.curheight,self.curwidth][self.curchan]
        val = int(val) & self.maskONE
        self.next_slot()
        if val > 0:
            return "1"
        else:
            return "0"
    
    def read_byte(self):
        return self.read_bits(8)
    
    def read_bits(self, nb): #Read the given number of bits
        bits = ""
        for i in range(nb):
            bits += self.read_bit()
        return bits

    def byteValue(self, val):
        return self.binary_value(val, 8)
        
    def binary_value(self, val, bitsize): #Return the binary value of an int as a byte
        binval = bin(val)[2:]
        if len(binval) > bitsize:
            raise SteganographyException("binary value larger than the expected size")
        while len(binval) < bitsize:
            binval = "0"+binval
        return binval
    
    def lsb_embed(self, data):
        l = len(data)
        max_cap = self.lsb_max_capacity()
        if max_cap < l+64:
            print("Payload size = ",(l+64)," Bytes")
            print("Image can hold up to ",max_cap," Bytes")
            raise SteganographyException("Payload is too large.")
        self.put_binary_value(self.binary_value(l, 64))
        for byte in data:
            byte = byte if isinstance(byte, int) else ord(byte) # Compat py2/py3
            self.put_binary_value(self.byteValue(byte))
        return self.image

    def lsb_extract(self):
        l = int(self.read_bits(64), 2)
        output = b""
        for i in range(l):
            output += bytearray([int(self.read_byte(),2,)])
        return output

def main(user_opt, image_name, payload):
    in_img = cv2.imread(image_name, cv2.IMREAD_COLOR)
    steg = Steg(in_img)

    if (user_opt == 'encode'):
        with open(payload, 'rb') as f:
            data = f.read()
        res = steg.lsb_embed(data)
        filename = input("Enter new image name(without extension): ")
        file = filename + ".png"
        cv2.imwrite(file, res)

    elif (user_opt == 'decode'):
        raw = steg.lsb_extract()
        with open(payload, "wb") as f:
            f.write(raw)

    else: 
        print(f"Unrecongnized mode {user_opt}. Aborting")
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
    main(user_opt, img_filename, payload_name)