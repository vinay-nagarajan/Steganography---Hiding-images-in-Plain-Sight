from os.path import join
import sys
import numpy as np
import base64
import re
import zlib
from scipy.misc import *
from PIL import Image

class Payload:
    def __init__(self,img=None, compressionLevel=-1, content=None):
        d = {}
        d['A'] = 0
        d['B'] = 1
        d['C'] = 2
        d['D'] = 3
        d['E'] = 4
        d['F'] = 5
        d['G'] = 6
        d['H'] = 7
        d['I'] = 8
        d['J'] = 9
        d['K'] = 10
        d['L'] = 11
        d['M'] = 12
        d['N'] = 13
        d['O'] = 14
        d['P'] = 15
        d['Q'] = 16
        d['R'] = 17
        d['S'] = 18
        d['T'] = 19
        d['U'] = 20
        d['V'] = 21
        d['W'] = 22
        d['X'] = 23
        d['Y'] = 24
        d['Z'] = 25
        d['a'] = 26
        d['b'] = 27
        d['c'] = 28
        d['d'] = 29
        d['e'] = 30
        d['f'] = 31
        d['g'] = 32
        d['h'] = 33
        d['i'] = 34
        d['j'] = 35
        d['k'] = 36
        d['l'] = 37
        d['m'] = 38
        d['n'] = 39
        d['o'] = 40
        d['p'] = 41
        d['q'] = 42
        d['r'] = 43
        d['s'] = 44
        d['t'] = 45
        d['u'] = 46
        d['v'] = 47
        d['w'] = 48
        d['x'] = 49
        d['y'] = 50
        d['z'] = 51
        d['0'] = 52
        d['1'] = 53
        d['2'] = 54
        d['3'] = 55
        d['4'] = 56
        d['5'] = 57
        d['6'] = 58
        d['7'] = 59
        d['8'] = 60
        d['9'] = 61
        d['+'] = 62
        d['/'] = 63

        if img is not None and content is None:
            if type(img) is not np.ndarray:
                raise TypeError("Type not correct")
            if compressionLevel <-1 or compressionLevel >9:
                raise ValueError("Provide appropriate compressionLevel value")
            else:
                self.img = img
                self.comp = compressionLevel
                if len(self.img.shape) == 3:
                    self.item = "Color"
                else:
                    self.item = "Gray"
                self.content = np.array(self.imgtocontent(d),dtype=np.uint8)
        elif img is None and content is not None:
            if type(content) is not np.ndarray:
                raise TypeError("Type not correct")
            self.content = content
            self.comp = compressionLevel
            self.img = self.contenttoimg(d)
        else:
            raise ValueError("Provide appropriate input")

    def imgtocontent(self,d):
        content = '<?xml version="1.0" encoding="UTF-8"?>'
        if self.comp == -1:
            content += '<payload type="'+self.item+'" size="'+str(self.img.shape[0])+','+str(self.img.shape[1])+'" compressed="False">'
            if self.item == "Color":
                b = np.append(np.append(self.img[:,:,0].flatten(), self.img[:,:,1].flatten()),self.img[:,:,2].flatten())
                content += ','.join(map(str, b))
                content += '</payload>'
                encoded = str(base64.b64encode(content.encode('utf-8')))[2:-1]
                q = list(encoded)
                q2 = list(map(d.get, q))
                q2 = list(filter(lambda v: v is not None, q2))


            else:
                b = np.ndarray.flatten(self.img)
                content += ','.join(map(str, b))

                content += '</payload>'

                encoded = str(base64.b64encode(content.encode('utf-8')))[2:-1]
                q = list(encoded)
                q2 = list(map(d.get, q))
                q2 = list(filter(lambda v: v is not None, q2))


        else:
            content += '<payload type="'+self.item+'" size="'+str(self.img.shape[0])+','+str(self.img.shape[1])+'" compressed="True">'
            if self.item == "Color":
                c = np.append(np.append(self.img[:,:,0].flatten(), self.img[:,:,1].flatten()),self.img[:,:,2].flatten())
                b = zlib.compress(c,self.comp)

                content += ','.join(map(str, b))


                content += '</payload>'
                encoded = str(base64.b64encode(content.encode('utf-8')))[2:-1]
                q = list(encoded)
                q2 = list(map(d.get, q))
                q2 = list(filter(lambda v: v is not None, q2))

            else:
                c = np.ndarray.flatten(self.img)
                b = zlib.compress(c,self.comp)
                content += ','.join(map(str, b))

                content += '</payload>'

                encoded = str(base64.b64encode(content.encode('utf-8')))[2:-1]
                q = list(encoded)
                q2 = list(map(d.get, q))
                q2 = list(filter(lambda v: v is not None, q2))


        return q2

    def contenttoimg(self,d):

        d2 = dict(zip(d.values(), d.keys()))
        #a = list(self.content)
        a = np.vectorize(d2.get)(self.content)

        str1 = ''.join(a)

        if(len(str1) % 4 != 0):
            str1 += '='
        if(len(str1) % 4 != 0):
            str1 += '='
        if(len(str1) % 4 != 0):
            str1 += '='


        #str1 = "TW9uZGF5"
        decoded = base64.b64decode(str1).decode('latin-1')
        s = decoded.find('</payload>')
        decoded = decoded[0:s+len('</payload>')]

        expr = r'<payload type="([A-Za-z]+)" size="([0-9]+),([0-9]+)" compressed="([A-Za-z]+)">(.+)</payload>'
        a = re.search(expr,decoded)
        if a:
            pt = a.groups()[0]
            r = a.groups()[1]
            r = int(r)
            c = a.groups()[2]
            c = int(c)
            comp = a.groups()[3]


            tempimg = np.fromstring(a.groups()[4], sep=',', dtype=np.uint8)

            if comp == "True":
                s = zlib.decompress(tempimg)
                decomp = np.fromstring(s,dtype=np.uint8)
            else:
                decomp = tempimg

            if pt == "Color":
                tempimg3 = np.dstack(tuple(decomp.reshape(3,-1)))
                tempimg3 = tempimg3.reshape(r,c,3)
            else:
                tempimg3 = decomp.reshape(r,c)

            return tempimg3


class Carrier:
    def __init__(self,img):
        if(type(img) is not np.ndarray):
            raise TypeError("Error")
        else:
            self.img = img


    def clean(self):
        l = self.img.flatten()
        bits = np.unpackbits(l[:,np.newaxis],axis=1)
        bits[:,-2:] = np.random.randint(0,2,size=(bits.shape[0],2))
        q = np.squeeze(np.packbits(bits,axis=1))
        (r,c,c2) = self.img.shape
        return q.reshape(r,c,3)




    def payloadExists(self):
        d = {}
        d['A'] = 0
        d['B'] = 1
        d['C'] = 2
        d['D'] = 3
        d['E'] = 4
        d['F'] = 5
        d['G'] = 6
        d['H'] = 7
        d['I'] = 8
        d['J'] = 9
        d['K'] = 10
        d['L'] = 11
        d['M'] = 12
        d['N'] = 13
        d['O'] = 14
        d['P'] = 15
        d['Q'] = 16
        d['R'] = 17
        d['S'] = 18
        d['T'] = 19
        d['U'] = 20
        d['V'] = 21
        d['W'] = 22
        d['X'] = 23
        d['Y'] = 24
        d['Z'] = 25
        d['a'] = 26
        d['b'] = 27
        d['c'] = 28
        d['d'] = 29
        d['e'] = 30
        d['f'] = 31
        d['g'] = 32
        d['h'] = 33
        d['i'] = 34
        d['j'] = 35
        d['k'] = 36
        d['l'] = 37
        d['m'] = 38
        d['n'] = 39
        d['o'] = 40
        d['p'] = 41
        d['q'] = 42
        d['r'] = 43
        d['s'] = 44
        d['t'] = 45
        d['u'] = 46
        d['v'] = 47
        d['w'] = 48
        d['x'] = 49
        d['y'] = 50
        d['z'] = 51
        d['0'] = 52
        d['1'] = 53
        d['2'] = 54
        d['3'] = 55
        d['4'] = 56
        d['5'] = 57
        d['6'] = 58
        d['7'] = 59
        d['8'] = 60
        d['9'] = 61
        d['+'] = 62
        d['/'] = 63

        d2 = dict(zip(d.values(), d.keys()))

        if len(self.img.shape) == 3:

            self.item = "Color"
        else:
            self.item = "Gray"

        if(self.item is "Color"):


            a = self.img[0]
            red_org = a[:,0].flatten() & 0b11
            green_org = a[:,1].flatten() & 0b11
            blue_org = a[:,2].flatten() & 0b11

            blue = blue_org << 4
            green = green_org << 2
            red = red_org
            new = blue | green | red

            a = np.vectorize(d2.get)(new)

            str1 = ''.join(a)


            if(len(str1) % 4 != 0):
                str1 += '='
            if(len(str1) % 4 != 0):
                str1 += '='
            if(len(str1) % 4 != 0):
                str1 += '='
            decoded = base64.b64decode(str1).decode('latin-1')
            if(decoded[0] == '<'):
                return True
            else:
                return False
        else:
            a = self.img[0].flatten() & 0b11
            a = np.reshape(a, (-1,3))

            red_org = a[:,0].flatten() & 0b11
            green_org = a[:,1].flatten() & 0b11
            blue_org = a[:,2].flatten() & 0b11

            blue = blue_org << 4
            green = green_org << 2
            red = red_org
            new = blue | green | red

            a = np.vectorize(d2.get)(new)

            str1 = ''.join(a)

            if(len(str1) % 4 != 0):
                str1 += '='
            if(len(str1) % 4 != 0):
                str1 += '='
            if(len(str1) % 4 != 0):
                str1 += '='
            decoded = base64.b64decode(str1).decode('latin-1')
            if(decoded[0] == '<'):
                return True
            else:
                return False


    def embedPayload(self, payload, override=False):
        if type(payload) != Payload:
                raise TypeError


        if(len(payload.content) *3 > len(self.img.flatten())):
            raise ValueError

        if(override == False):
            check = self.payloadExists()
            if(check == True):
                raise Exception
            else:
                embedd = 1
        if(embedd == 1 or override == True):

            if len(self.img.shape) == 3:

                self.item = "Color"
            else:
                self.item = "Gray"

            if(self.item == "Color"):
                (r,c,q) = self.img.shape

                red_org = self.img[:,:,0].flatten()
                red = red_org[:len(payload.content * 3)]
                red_left = red_org[len(payload.content * 3):]
                green_org = self.img[:,:,1].flatten()
                green = green_org[:len(payload.content * 3)]
                green_left = green_org[len(payload.content * 3):]
                blue_org = self.img[:,:,2].flatten()
                blue = blue_org[:len(payload.content * 3)]
                blue_left = blue_org[len(payload.content * 3):]

                red  = red & 252
                green = green & 252
                blue = blue & 252

                temp1 = (payload.content) & 0b00000011
                temp2 = (payload.content >> 2) & 0b00000011
                temp3 = (payload.content >> 4) & 0b00000011

                red = red | temp1
                green = green | temp2
                blue = blue | temp3

                red = np.concatenate((red,red_left))
                green = np.concatenate((green,green_left))
                blue = np.concatenate((blue,blue_left))

                #b = np.array([red,green,blue])
                tempimg3 = np.array([red,green,blue])

                #red = np.concatenate((red,green))
                #tempimg3 = np.concatenate((red,blue))
                tempimg3 = tempimg3.reshape(3,-1)
                tempimg3 = np.dstack(tuple(tempimg3))
                tempimg3 = tempimg3.reshape(r,c,3)
                return tempimg3

            else:
                (r,c) = self.img.shape
                self.img2 = np.reshape(self.img.flatten(), (-1,3))
                red_org = self.img2[:,0].flatten()
                red = red_org[:len(payload.content * 3)]
                red_left = red_org[len(payload.content * 3):]
                green_org = self.img2[:,1].flatten()
                green = green_org[:len(payload.content * 3)]
                green_left = green_org[len(payload.content * 3):]
                blue_org = self.img2[:,2].flatten()
                blue = blue_org[:len(payload.content * 3)]
                blue_left = blue_org[len(payload.content * 3):]

                red  = red & 252
                green = green & 252
                blue = blue & 252

                temp1 = (payload.content) & 0b00000011
                temp2 = (payload.content >> 2) & 0b00000011
                temp3 = (payload.content >> 4) & 0b00000011

                red = red | temp1
                green = green | temp2
                blue = blue | temp3

                red = np.concatenate((red,red_left))
                green = np.concatenate((green,green_left))
                blue = np.concatenate((blue,blue_left))

                #b = np.array([red,green,blue])
                tempimg3 = np.array([red,green,blue])
                tempimg3 = np.dstack(tuple(tempimg3))

                tempimg3 = tempimg3.reshape(r,c)
                #red = np.concatenate((red,green))
                #tempimg3 = np.concatenate((red,blue))

                return tempimg3



    def extractPayload(self):

        if self.payloadExists() is True:
            if len(self.img.shape) == 3:

                self.item = "Color"
            else:
                self.item = "Gray"

            if(self.item is "Color"):

                red_org = self.img[:,:,0].flatten() & 0b11
                green_org = self.img[:,:,1].flatten() & 0b11
                blue_org = self.img[:,:,2].flatten() & 0b11

                blue = blue_org << 4
                green = green_org << 2
                red = red_org
                new = blue | green | red
                return Payload(content = new)
            else:
                a = self.img.flatten() & 0b11
                a = np.reshape(a, (-1,3))

                red_org = a[:,0].flatten() & 0b11
                green_org = a[:,1].flatten() & 0b11
                blue_org = a[:,2].flatten() & 0b11

                blue = blue_org << 4
                green = green_org << 2
                red = red_org
                new = blue | green | red
                return Payload(content = new)

        else:
            raise Exception

                #a.reshape(len(a))



if __name__== "__main__":
    pass






