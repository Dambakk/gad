#!/usr/local/bin/env python3
import os
import argparse
import json
from PIL import Image, ImageFilter
from colorama import Fore, Back, Style
import configparser

#Constants
pathToConfig = "imageParser/colorTypes.ini"
HTML = 0
IOS = 1
ANDROID = 2

# Colors with the corresponding types
colorTypes = {}

def parseImage(path, outputPath, platform, debug):
    image = Image.open(path)
    pixels = image.load()
    width, height = image.size

    if debug : print(Fore.GREEN + "Image loaded successfully" + Style.RESET_ALL)
      
    Config = configparser.RawConfigParser()
    Config.read(pathToConfig)
    print()
    if debug : 
        print(Fore.GREEN + "Config files loaded successfully" + Style.RESET_ALL)
        
    readConfigFile(Config)

    CompleteRGBDict = PixelSearcher(height, width, image)

    jsonPath = JSONObjects(CompleteRGBDict, outputPath)

    return jsonPath

def readConfigFile(config):
    options = config.options("color")
    for option in options:
        colorTypes["#" + option] = eval(config.get("color", option))


# RGBA, not taking into account the a, yet which will be the transparent parameter
"""
    Function that searchs through the different pixels - returning the elements
"""

def PixelSearcher(height, width, image):

    RGBCornerPixels = {}
    number = 0

    for x in range(0, height):
        zValue = 0
        currentColor = -1,-1,-1
        isWhite = False
        for y in range(0, width):
            r,g,b,a = image.getpixel((y, x))
            if (r != 255 or g != 255 or b != 255):
                if(x < height and y < width and x > 0 and y > 0):
                    RGB = r,g,b
                    if(RGB != currentColor):
                        zValue = FindZValue(zValue, x, y, image, RGBCornerPixels, RGB, isWhite)
                        currentColor = RGB
                    isWhite = CheckIfCorner(RGBCornerPixels, x, y, image, number, RGB, zValue, isWhite)

    return RGBCornerPixels

"""
Funksjon som finner ut om vi har et hjørne, må oppdatteres for å takle nesting
"""

def CheckIfCorner(RGBCornerPixels, x,y, image, number, RGB, zValue, isWhite):
    value1,value2,value3 = RGB
    r,g,b,a = image.getpixel((y, x-1))
    c,d,e,f = image.getpixel((y-1, x))
    if(r == 255 and g == 255 and b == 255 and c == 255 and d == 255 and e == 255):
        try:
            RGBCornerPixels[value1,value2,value3].append([x,y, zValue])
        except KeyError:
            RGBCornerPixels[value1,value2,value3] = [[x,y, zValue]]

    x1,x2,x3,x4 = image.getpixel((y+1, x))
    z1,z2,z3,z4 = image.getpixel((y, x-1))
    if(x1 == 255 and x2 == 255 and x3 == 255 and z1 == 255 and z2 == 255 and z3 == 255):
        RGBCornerPixels[value1,value2,value3].append([x,y, zValue])
        isWhite = True

    x5,x6,x7,x8 = image.getpixel((y, x+1))
    z5,z6,z7,z8 = image.getpixel((y-1, x))
    if(x5 == 255 and x6 == 255 and x7 == 255 and z5 == 255 and z6 == 255 and z7 == 255):
        RGBCornerPixels[value1,value2,value3].append([x,y, zValue])

    x9, x10, x11, x12 = image.getpixel((y+1, x))
    z9,z10,z11,z12 = image.getpixel((y, x+1))
    if(x9 == 255 and x10 == 255 and x11 == 255 and z9 == 255 and z10 == 255 and z11 == 255):
        RGBCornerPixels[value1,value2,value3].append([x,y, zValue])

    return isWhite

#Testing at the moment
def FindZValue(Zvalue, x, y, image, RGBCornerPixels, RGB, isWhite):
    r,g,b,a = image.getpixel((y-1, x))

    if(r != 225 and g != 255 and b != 255):
        Zvalue += 1
    if(RGB in RGBCornerPixels and isWhite == True):
        Zvalue -= 1
    if(isWhite == True):
        Zvalue = 0

    return Zvalue



def ConvertToHex(rgbColor):
    hexValue = '#%02x%02x%02x' % (rgbColor[0], rgbColor[1], rgbColor[2])
    return hexValue


def getType(color, platform):
    if colorTypes.get(color):
        return colorTypes[color][platform]
    else:
        print(Fore.RED + "Color is not known and ignored: " +  Style.RESET_ALL + color)
        return None

def JSONObjects(CompleteRGBDict, outputPath):

    objects = []
    ListToSaveJSONObjects = []

    while(len(CompleteRGBDict) != 0):
        squaresList = []
        num = CompleteRGBDict.popitem()
        rgbColor = num[0]
        num2 = num[1]
        findTheSquares(num2, squaresList)
        objects.append([rgbColor, squaresList])


    while(len(objects) != 0):
        theFinalList = objects.pop(0)
        firstValue = theFinalList.pop(0)
        secondValue = theFinalList[0]

        hexValue = ConvertToHex(firstValue)


        for i in range(len(secondValue)):
            first = secondValue[i][0]
            second = secondValue[i][1]
            third = secondValue[i][2]
            fourth = secondValue[i][3]
            elements = [first, second, third, fourth]
            path = JSONMakerAndSaver(elements, hexValue, ListToSaveJSONObjects, outputPath)

    return path

"""
    Takes the different boxes, one at a time and creates a JSON objects. Then it saves it to a file
"""
def JSONMakerAndSaver(elements, hexValue, ListToSaveJSONObjects, outputPath):
    data = {}

    data['content'] = "Color code: " + hexValue
    data['color'] = hexValue
    data['type'] = getType(hexValue, 0)
    data['y'] = elements[0][0]
    data['x'] = elements[0][1]
    data['width'] = elements[1][1] - elements[0][1]
    data['height'] = elements[2][0] - elements[0][0]
    ListToSaveJSONObjects.append(data)
    
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
        f = open(outputPath+"/imageRepresentation.json", "w+")
        json.dump(ListToSaveJSONObjects, f)
        f.close
    else:
        f = open(outputPath+"/imageRepresentation.json", "w+")
        json.dump(ListToSaveJSONObjects, f)
        f.close

    return outputPath + "/imageRepresentation.json"



"""
    Finds the four corners of the given box.
"""

def findTheSquares(corners, squaresList):

    while len(corners) != 0:
        firstCorner = corners[0]
        secondCorner = corners[1]
        corners.pop(0)
        corners.pop(0)

        value1, value2 = findEndCorners(corners, firstCorner, secondCorner)

        thirdCorner = corners[value1]
        fourthCorner = corners[value2]

        del corners[value1:value2+1]

        squaresList.append([firstCorner,secondCorner, thirdCorner, fourthCorner])

"""
    Helper function to find the end corners
"""

def findEndCorners(corners, firstCorner, secondCorner):
    firstValue = 0
    secondValue = 0
    number = 0
    for i in corners:
        if(i[1] == firstCorner[1]):
            firstValue = number
        if(i[1] == secondCorner[1]):
            secondValue = number
            break
        number += 1

    returnValue = firstValue,secondValue

    return returnValue




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

    pathToConfig = "colorTypes.ini"

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
    print("Image parser: " + Fore.GREEN + "Done" + Style.RESET_ALL)


