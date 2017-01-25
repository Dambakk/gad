#!/usr/local/bin/env python3
import argparse
import json
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("ImagePath", help="Path to image")

args = ap.parse_args()

print("Image path: " + args.ImagePath)



#image = image.filter(ImageFilter.FIND_EDGES)
#image.save('newImage.png')

image = Image.open(args.ImagePath)
image = image.convert('RGB')

pixels = image.load()
width, height = image.size

#print(width)
#print(height)
#print(pixels)
mydict = []
dictionary = {}

def MyFunc(dictionary):
    number = 0
    for x in range(0, height):
        for y in range(0, width):
            r,g,b = image.getpixel((y, x))
            print(r,g,b, "    ", x, y)
            if (r and g and b != 255):
                try:
                    dictionary[r,g,b].append([x,y])
                except KeyError:
                    dictionary[r,g,b] = [[x,y]]
                myitem = (x, y, " ", r,g,b)
                mydict.append(myitem)
                number += 1
        print(" ")
    print(number)


MyFunc(dictionary)


num = dictionary.popitem()
rgbColor = num[0]
num2 = num[1]



print(dictionary)
print(len(dictionary))
print(num[0])
print(num[1])
print(len(num2))
print(num2[0])
print(num2[len(num2)-1])

sStart = num2[0]
sEnd = num2[len(num2)-1]

#print(sStart[0])
#print(sEnd[0])

#Height is x, Width is y
def FindSquare(sStart, sEnd):
    tHeight = sEnd[0] - sStart[0]
    tWidth = sEnd[1] - sStart[1]

    print(tHeight)
    print(tWidth)

    tup1 = (tHeight, tWidth)
    return tup1

squareResult = FindSquare(sStart, sEnd)


def ConvertToHex(rgbColor):
    hexValue = '#%02x%02x%02x' % (rgbColor[0], rgbColor[1], rgbColor[2])
    return hexValue

hexVal = ConvertToHex(rgbColor)

#myList = {rgbColor}

newList = []

def MakingJSONObject(squareResult, hexVal, sStart, newList):

    data = {}
    data['type'] = 'div'
    data['content'] = "empty"
    data['color'] = hexVal
    data['y'] = sStart[0]
    data['x'] = sStart[1]
    data['width'] = squareResult[1]
    data['height'] = squareResult[0]
    newList.append(data)
    print(newList)

MakingJSONObject(squareResult, hexVal, sStart, newList)




















print("Done")
