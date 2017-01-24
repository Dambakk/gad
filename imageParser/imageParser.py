#!/usr/local/bin/env python3
import os
import argparse
import json
from PIL import Image, ImageFilter
from colorama import Fore, Back, Style
import configparser


pathToConfig = "imageParser/colorTypes.ini"
#Constants
HTML = 0
IOS = 1
ANDROID = 2

# Colors with the corresponding types
colorTypes = {}
#colorTypes['#15aaff'] = ('div', 'iOsType', 'javaType') # blue
#colorTypes['#fb0007'] = ('p', 'iOsType', 'javaType') # red


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
        #print("Sections: " + Config.sections())

    readConfigFile(Config)


    mydict = []
    dictionary = {}

    newDict = MyFunc(dictionary, height, width, image, mydict)


    finalDictionary = newDict[1]

    print(finalDictionary)

    newList = []

    #print(newDict)

    jsonPath = makeJSONObjects(finalDictionary, outputPath)

    """
    for i in range(len(newDict)):

        num = dictionary.popitem()
        rgbColor = num[0]
        num2 = num[1]

        sStart = num2[0]
        sEnd = num2[len(num2)-1]

        squareResult = FindSquare(sStart, sEnd)

        hexVal = ConvertToHex(rgbColor)

        jsonPath = MakingJSONObject(squareResult, hexVal, sStart, newList, outputPath, platform)
    """

    print(jsonPath)
    return jsonPath


def readConfigFile(config):
    options = config.options("color")
    for option in options:
        colorTypes["#" + option] = eval(config.get("color", option))

    #Put other readings here...


# RGBA, not taking into account the a, yet which will be the transparent parameter
def MyFunc(dictionary, height, width, image, mydict):

    newDictionary = {}
    number = 0

    for x in range(0, height):
        zValue = 0
        currentColor = -1,-1,-1
        isWhite = False
        for y in range(0, width):

            r,g,b,a = image.getpixel((y, x))
            #print(r,g,b, "    ", x, y)
            if (r != 255 or g != 255 or b != 255):
                try:
                    dictionary[r,g,b].append([x,y])
                except KeyError:
                    dictionary[r,g,b] = [[x,y]]

                if(x < height and y < width and x > 0 and y > 0):

                    RGB = r,g,b
                    if(RGB != currentColor):
                        zValue = FindZValue(zValue, x, y, image, newDictionary, RGB, isWhite)
                        currentColor = RGB
                        print(zValue)
                    isWhite = ReturnElement(newDictionary, x, y, image, number, RGB, zValue, isWhite)

                #myitem = (x, y, " ", r,g,b)
                #mydict.append(myitem)
    #print(newDictionary)
    newThing = [dictionary, newDictionary]
    return newThing

def ReturnElement(newDictionary, x,y, image, number, RGB, zValue, isWhite):
    value1,value2,value3 = RGB
    r,g,b,a = image.getpixel((y, x-1))
    c,d,e,f = image.getpixel((y-1, x))
    if(r == 255 and g == 255 and b == 255 and c == 255 and d == 255 and e == 255):
        try:
            newDictionary[value1,value2,value3].append([x,y, zValue])
        except KeyError:
            newDictionary[value1,value2,value3] = [[x,y, zValue]]

    x1,x2,x3,x4 = image.getpixel((y+1, x))
    z1,z2,z3,z4 = image.getpixel((y, x-1))
    if(x1 == 255 and x2 == 255 and x3 == 255 and z1 == 255 and z2 == 255 and z3 == 255):
        newDictionary[value1,value2,value3].append([x,y, zValue])
        isWhite = True

    x5,x6,x7,x8 = image.getpixel((y, x+1))
    z5,z6,z7,z8 = image.getpixel((y-1, x))
    if(x5 == 255 and x6 == 255 and x7 == 255 and z5 == 255 and z6 == 255 and z7 == 255):
        newDictionary[value1,value2,value3].append([x,y, zValue])

    x9, x10, x11, x12 = image.getpixel((y+1, x))
    z9,z10,z11,z12 = image.getpixel((y, x+1))
    if(x9 == 255 and x10 == 255 and x11 == 255 and z9 == 255 and z10 == 255 and z11 == 255):
        newDictionary[value1,value2,value3].append([x,y, zValue])

    return isWhite


def FindZValue(Zvalue, x, y, image, newDictionary, RGB, isWhite):
    r,g,b,a = image.getpixel((y-1, x))

    if(r != 225 and g != 255 and b != 255):
        Zvalue += 1
    if(RGB in newDictionary and isWhite == True):
        Zvalue -= 1
    if(isWhite == True):
        Zvalue = 0

    return Zvalue





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

def makeJSONObjects(finalDictionary, outputPath):

    objects = []

    mnewList = []
    while(len(finalDictionary) != 0):
        squaresList = []
        num = finalDictionary.popitem()
        rgbColor = num[0]
        print(rgbColor, "rgbColor")
        num2 = num[1]
        print(num2)

        findTheSquares(num2, squaresList)

        objects.append([rgbColor, squaresList])
        #objects.append([rgbColor, squaresList])

    print(objects[0])

    JSONList = objects[0]
    hexValue = ConvertToHex(JSONList.pop(0))

    print(len(JSONList[0]))

    while(len(JSONList[0]) != 0):

        newList = JSONList[0].pop(0)
        print(newList)

        print(hexValue)

        path = makeJSONObjectsFinal(newList, hexValue, mnewList, outputPath)

    return path


def makeJSONObjectsFinal(item, hexValue, newList, outputPath):
    data = {}
    #data['type'] = 'div'
    #data['type'] = getType(hexVal, platform) # color, targetPlatform
    #if data['type'] is None: return
    data['content'] = "Color code: " + hexValue
    data['color'] = hexValue
    data['type'] = getType(hexValue, 0)
    data['y'] = item[0][0]
    print(item[0][0])
    data['x'] = item[0][1]
    print(item[0][1])
    data['width'] = item[1][1] - item[0][1]
    data['height'] = item[2][0] - item[0][0]
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







def findTheSquares(corners, squaresList):

    while len(corners) != 0:
        firstNumber = corners[0]
        secondNumber = corners[1]
        corners.pop(0)
        corners.pop(0)

        value1, value2 = findLastCorners(corners, firstNumber, secondNumber)

        thirdNumber = corners[value1]
        fourthNumber = corners[value2]

        del corners[value1:value2+1]
        #del corners[value2]

        #print(corners)

        print("-----------")
        print(firstNumber)
        print(secondNumber)
        print(thirdNumber)
        print(fourthNumber)
        print("-----------")

        print(len(corners))
        print(corners)

        squaresList.append([firstNumber,secondNumber, thirdNumber, fourthNumber])






def findLastCorners(corners, firstNumber, secondNumber):
    firstValue = 0
    secondValue = 0
    number = 0
    for i in corners:
        if(i[1] == firstNumber[1]):
            firstValue = number
        if(i[1] == secondNumber[1]):
            secondValue = number
            break
        number += 1

    returnValue = firstValue,secondValue
    print(returnValue, " returnvalue")

    return returnValue





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


