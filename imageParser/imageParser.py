#!/usr/local/bin/env python3
import os
import argparse
import json
from PIL import Image, ImageFilter
from colorama import Fore, Back, Style

#Constants
HTML = 0
IOS = 1
ANDROID = 2

# Colors with the corresponding types
colorTypes = {}
colorTypes['#15aaff'] = ('div', 'iOsType', 'javaType') # blue
colorTypes['#fb0007'] = ('p', 'iOsType', 'javaType') # red


def parseImage(path, outputPath, platform, debug):
    image = Image.open(path)
    pixels = image.load()
    width, height = image.size

    if debug : print(Fore.YELLOW + "Image loaded successfully" + Style.RESET_ALL)

    mydict = []
    dictionary = {}

    newDict = MyFunc(dictionary, height, width, image, mydict)

    newList = []

    for i in range(len(newDict)):

        num = dictionary.popitem()
        rgbColor = num[0]
        num2 = num[1]

        sStart = num2[0]
        sEnd = num2[len(num2)-1]

        squareResult = FindSquare(sStart, sEnd)

        hexVal = ConvertToHex(rgbColor)

        jsonPath = MakingJSONObject(squareResult, hexVal, sStart, newList, outputPath, platform)

    return jsonPath

# RGBA, not taking into account the a, yet which will be the transparent parameter
def MyFunc(dictionary, height, width, image, mydict):
    number = 0
    for x in range(0, height):
        for y in range(0, width):
            r,g,b,a = image.getpixel((y, x))
            #print(r,g,b, "    ", x, y)
            if (r != 255 or g != 255 or b != 255):
                try:
                    dictionary[r,g,b].append([x,y])
                except KeyError:
                    dictionary[r,g,b] = [[x,y]]
                myitem = (x, y, " ", r,g,b)
                mydict.append(myitem)
                number += 1
        #print(" ")
    return dictionary


def FindSquare(sStart, sEnd):
    tHeight = sEnd[0] - sStart[0]
    tWidth = sEnd[1] - sStart[1]

    #print(tHeight)
    #print(tWidth)

    tup1 = (tHeight, tWidth)
    return tup1


def ConvertToHex(rgbColor):
    hexValue = '#%02x%02x%02x' % (rgbColor[0], rgbColor[1], rgbColor[2])
    return hexValue


def getType(color, platform):
    if colorTypes.get(color):
        return colorTypes[color][platform]
    else: 
        print(Fore.RED + "Color is not known and ignored: " +  Style.RESET_ALL + color)
        return None 



def MakingJSONObject(squareResult, hexVal, sStart, newList, outputPath, platform):

    data = {}
    #data['type'] = 'div'
    data['type'] = getType(hexVal, platform) # color, targetPlatform
    if data['type'] is None: return
    data['content'] = "Color code: " + hexVal
    data['color'] = hexVal
    data['y'] = sStart[0]
    data['x'] = sStart[1]
    data['width'] = squareResult[1]
    data['height'] = squareResult[0]
    newList.append(data)
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
        f = open(outputPath+"/imageRepresentation.json", "w+")
        json.dump(newList, f)
        f.close
    else:
        f = open(outputPath+"/imageRepresentation.json", "w+")
        json.dump(newList, f)
        f.close

    return outputPath + "/imageRepresentation.json"


if __name__== "__main__":
    ap = argparse.ArgumentParser()
    
    ap.add_argument("inputImage", help="Path to selected image")
    ap.add_argument("outputPath", help="Path to output directory")

    platform = ap.add_mutually_exclusive_group(required=True)
    platform.add_argument("--ios", help="Create a iOs project", action="store_true")
    platform.add_argument("--html", help="Create a html web page", action="store_true")
    platform.add_argument("--android", help="Create an android project", action="store_true")

    ap.add_argument("-v", "--verbose", help="Verbose output level", action="store_true", default=False)

    args = ap.parse_args()

    if not(args.inputImage.lower().endswith(".png")):
    	print(Fore.RED + "File should be an image file (png)." + Style.RESET_ALL)
    else:
        path = os.path.abspath(args.inputImage)
        outputPath = os.path.abspath(args.outputPath)
        platform = -1
        if args.ios: 
            platform = IOS
        elif args.html:
            platform = HTML 
        elif args.android:
            platform = ANDROID
        parseImage(path, outputPath, platform, args.verbose)


print(Fore.GREEN + "Image parser: " + Style.RESET_ALL +"Done" )
