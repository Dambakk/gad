#!/usr/local/bin/env python3
import os
import argparse
import json
from PIL import Image, ImageFilter








def parseImage(path, outputPath):
    image = Image.open(path)
    pixels = image.load()
    width, height = image.size
    print("Received image ")

    mydict = []
    dictionary = {}

    newDict = MyFunc(dictionary, height, width, image, mydict)


    newList = []

    print(len(newDict))

    for i in range(len(newDict)):

        num = dictionary.popitem()
        rgbColor = num[0]
        num2 = num[1]

        sStart = num2[0]
        sEnd = num2[len(num2)-1]

        squareResult = FindSquare(sStart, sEnd)

        hexVal = ConvertToHex(rgbColor)

        MakingJSONObject(squareResult, hexVal, sStart, newList, outputPath)

    return newList

# RGBA, not taking into account the a, yet which will be the transparent parameter
def MyFunc(dictionary, height, width, image, mydict):
    number = 0
    for x in range(0, height):
        for y in range(0, width):
            r,g,b,a = image.getpixel((y, x))
            print(r,g,b, "    ", x, y)
            if (r != 255 or g != 255 or b != 255):
                try:
                    dictionary[r,g,b].append([x,y])
                except KeyError:
                    dictionary[r,g,b] = [[x,y]]
                myitem = (x, y, " ", r,g,b)
                mydict.append(myitem)
                number += 1
        print(" ")
    return dictionary


def FindSquare(sStart, sEnd):
    tHeight = sEnd[0] - sStart[0]
    tWidth = sEnd[1] - sStart[1]

    print(tHeight)
    print(tWidth)

    tup1 = (tHeight, tWidth)
    return tup1


def ConvertToHex(rgbColor):
    hexValue = '#%02x%02x%02x' % (rgbColor[0], rgbColor[1], rgbColor[2])
    return hexValue



def MakingJSONObject(squareResult, hexVal, sStart, newList, outputPath):

    data = {}
    data['type'] = 'div'
    data['content'] = "Hei"
    data['color'] = hexVal
    data['y'] = sStart[0]
    data['x'] = sStart[1]
    data['width'] = squareResult[1]
    data['height'] = squareResult[0]
    newList.append(data)
    if not os.path.exists(args.outputPath):
        os.makedirs(outputPath)
        f = open(outputPath+"/testFil.json", "w+")
        json.dump(newList, f)
        f.close
    else:
        f = open(outputPath+"/testFil.json", "w+")
        json.dump(newList, f)
        f.close

    return outputPath


if __name__== "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inputImage", help="Path to selected image")
    ap.add_argument("outputPath", help="Path to output directory")
    args = ap.parse_args()

    print(args.inputImage)

    if not(args.inputImage.lower().endswith(".png")):
    	print("File should be an image file (png)")
    else:
        path = os.path.abspath(args.inputImage)
        outputPath = os.path.abspath(args.outputPath)
        parseImage(path, outputPath)




print("Done")
