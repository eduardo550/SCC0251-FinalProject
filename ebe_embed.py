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
        self.sobel_x, self.sobel_y = get_sobel(im)
        self.height, self.width, self.nbchannels = im.shape
        self.size = self.width * self.height
        
        self.maskONEValues = [1,2]
        #Mask used to put one ex:1->00000001, 2->00000010 .. associated with OR bitwise
        self.maskONE = self.maskONEValues.pop(0) #Will be used to do bitwise operations
        
        self.maskZEROValues = [254,253]
        #Mask used to put zero ex:254->11111110, 253->11111101 .. associated with AND bitwise
        self.maskZERO = self.maskZEROValues.pop(0)
        
        self.curwidth = 0  # Current width position
        self.curheight = 0 # Current height position
        self.curchan = 0   # Current channel position
        
    def next_slot(self):#Move to the next slot were information can be taken or put
        if self.curchan == self.nbchannels-1:
            self.curchan = 0 #Next Space is the first channel of the next pixel
            if self.curwidth == self.width-1:
                self.curwidth = 0 #Next Space is the first pixel
                if self.curheight == self.height-1:
                    self.curheight = 0 #Next Space is the first line (Using the second bit now)
                    if self.maskONE == 2:
                        raise SteganographyException("No available slot remaining (image filled)")
                    else: #Or instead of using the first bit start using the second.
                        self.maskONE = self.maskONEValues.pop(0)
                        self.maskZERO = self.maskZEROValues.pop(0)
                else:
                    self.curheight +=1 #Next Space is the following line
            else:
                self.curwidth +=1 #Next Space is the following pixel of the same line
        else:
            self.curchan +=1 #Next Space is the following channel

    def put_binary_value(self, bits): #Put the bits in the image
        for c in bits:
            while self.gradient() < 50:
                self.next_slot()
            val = list(self.image[self.curheight,self.curwidth]) #Get the pixel value as a list
            if int(c) == 1:
                val[self.curchan] = int(val[self.curchan]) | self.maskONE #OR with maskONE
            else:
                val[self.curchan] = int(val[self.curchan]) & self.maskZERO #AND with maskZERO
                
            self.image[self.curheight,self.curwidth] = tuple(val)
            self.next_slot() #Move "cursor" to the next space
        return

    def gradient(self):
        x = self.sobel_x[self.curheight,self.curwidth]
        y = self.sobel_y[self.curheight,self.curwidth]
        return math.sqrt(x**2 + y**2)

    def max_capacity(self):
        ngrad = 0
        for x in range(self.width):
            for y in range(self.height):
                if math.sqrt(self.sobel_x[y,x]**2 + self.sobel_y[y,x]**2) > 49:
                    ngrad+=1
        return (ngrad*self.nbchannels)/4

    def read_bit(self): #Read a single bit into the image
        while self.gradient() < 50:
            self.next_slot()
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
    
    def embed(self, data):
        l = len(data)
        max_cap = self.max_capacity()
        if max_cap < l+64:
            print("Payload size = ",(l+64)," Bytes")
            print("Image can hold up to ",max_cap," Bytes")
            raise SteganographyException("Payload is too large.")
        self.put_binary_value(self.binary_value(l, 64))
        for byte in data:
            byte = byte if isinstance(byte, int) else ord(byte) # Compat py2/py3
            self.put_binary_value(self.byteValue(byte))
        return self.image

    def extract(self):
        l = int(self.read_bits(64), 2)
        output = b""
        for i in range(l):
            output += bytearray([int(self.read_byte(),2,)])
        return output

def get_sobel(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        sobel_y = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        return sobel_x, sobel_y

def main(user_opt, image_name, payload):
    in_img = cv2.imread(image_name, cv2.IMREAD_COLOR)
    steg = Steg(in_img)

    if (user_opt == 'encode'):
        with open(payload, 'rb') as f:
            data = f.read()
        res = steg.embed(data)
        filename = input("Enter new image name(without extension): ")
        file = filename + ".png"
        cv2.imwrite(file, res)

    elif (user_opt == 'decode'):
        raw = steg.extract()
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