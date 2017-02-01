#!/usr/local/bin/env python3
import os
import argparse
import json
from PIL import Image, ImageFilter
from colorama import Fore, Back, Style
import configparser
from collections import OrderedDict

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
    idValue = 0
    for x in range(0, height):
        zValue = 0
        currentColor = -1,-1,-1
        isWhite = False
        for y in range(0, width):
            r,g,b,a = image.getpixel((y, x))
            if (r != 255 or g != 255 or b != 255):
                if(x < height and y < width and x > 0 and y > 0):
                    RGB = r,g,b
                    CheckIfCorner(RGBCornerPixels, x, y, image, number, RGB, zValue, idValue)
    print(RGBCornerPixels)
    return RGBCornerPixels

"""
Funksjon som finner ut om vi har et hjørne, må oppdatteres for å takle nesting
"""

def CheckIfCorner(RGBCornerPixels, x,y, image, number, RGB, zValue, idValue):
    value1,value2,value3 = RGB
    r,g,b,a = image.getpixel((y, x-1))
    c,d,e,f = image.getpixel((y-1, x))
    RGB1 = r,g,b
    RGB2 = c,d,e

    if(RGB != RGB1 and RGB != RGB2):
        try:
            RGBCornerPixels[value1,value2,value3].append([x,y])
            #RGBCornerPixels[value1,value2,value3].append(idValue)
        except KeyError:
            RGBCornerPixels[value1,value2,value3] = [[x,y]]
            #RGBCornerPixels[value1,value2,value3].append(str(idValue))

    x1,x2,x3,x4 = image.getpixel((y+1, x))
    z1,z2,z3,z4 = image.getpixel((y, x-1))
    RGB3 = x1,x2,x3
    RGB4 = z1,z2,z3
    if(RGB != RGB3 and RGB != RGB4):
        RGBCornerPixels[value1,value2,value3].append([x,y])
        #RGBCornerPixels[value1,value2,value3].append(str(idValue))

    x5,x6,x7,x8 = image.getpixel((y, x+1))
    z5,z6,z7,z8 = image.getpixel((y-1, x))
    RGB5 = x5,x6,x7
    RGB6 = z5,z6,z7
    if(RGB != RGB5 and RGB != RGB6):
        RGBCornerPixels[value1,value2,value3].append([x,y])
        #RGBCornerPixels[value1,value2,value3].append(str(idValue))

    x9, x10, x11, x12 = image.getpixel((y+1, x))
    z9,z10,z11,z12 = image.getpixel((y, x+1))
    RGB7 = x9,x10,x11
    RGB8 = z9,z10,z11
    if(RGB != RGB7 and RGB != RGB8):
        RGBCornerPixels[value1,value2,value3].append([x,y])
        #RGBCornerPixels[value1,value2,value3].append(str(idValue))


def ConvertToHex(rgbColor):
    hexValue = '#%02x%02x%02x' % (rgbColor[0], rgbColor[1], rgbColor[2])
    return hexValue


def getType(color, platform):
    if colorTypes.get(color):
        return colorTypes[color][platform]
    else:
        print(Fore.RED + "Color is not known and ignored: " +  Style.RESET_ALL + color)
        return None

def listToOrderedList(L):
    print("input list: ", L)
    d = {}
    ol = [OrderedDict((k, d[k](v)) for (k, v) in l.items()) for l in L]
    print("Output list: ", ol)


def JSONObjects(CompleteRGBDict, outputPath):

    objects = []
    ListToSaveJSONObjects = []
    listToFindZValues = []
    completeList = []
    completeListOrdered = OrderedDict()

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
            elements = [hexValue,first, second, third, fourth]
            listToFindZValues.append(elements)
            #print(elements)
            #path = JSONMakerAndSaver(elements, hexValue, ListToSaveJSONObjects, outputPath)

    """
        Append different ID to all elements
    """
    idNumber = 0
    for x in listToFindZValues:
        x.append(str(idNumber))
        idNumber += 1


    #print(listToFindZValues)

    listToFindZValues = findZValues(listToFindZValues)

    #print(listToFindZValues)

    for i in range(len(listToFindZValues)):
        JSONMakerAndSaver(ListToSaveJSONObjects, listToFindZValues[i], completeList, completeListOrdered)

    print("COMPLETE LIST: ")
    #print(ListToSaveJSONObjects)
    for e in ListToSaveJSONObjects:
        print(e)
    #print(completeListOrdered)
    print("ALL ITEMS:")
    for l in completeListOrdered.items():
        print(l)
    print(ListToSaveJSONObjects)

    nestedList = fixNesting(completeListOrdered)
    #WriteToFile(ListToSaveJSONObjects, outputPath, completeList)
    WriteToFile(ListToSaveJSONObjects, outputPath, nestedList)

    return path


def fixNesting(completeListOrdered):
    print("")
    print("Fixing nesting: ")
    nestedList = OrderedDict()

    #Connect those with parents
    for e in completeListOrdered.items():
        parent = e[1]["parent"]
        print("Element: ", e)
        print("parent: ", parent)
        if parent is not -1:
            #print("parent is ", parent, " and the complete list is ", completeListOrdered)
            print("Parent element: ", completeListOrdered[str(parent)]['id'])
            numOfEl = len(completeListOrdered[str(parent)]["content"])
            print("Number of elements in content: ", numOfEl)
            completeListOrdered[str(parent)]["content"][numOfEl] = e
            print("parent updated: ", completeListOrdered[str(parent)])
            #print("new nested element: ", completeListOrdered[parent])

    #Remove those with parents from outer scope

    #Done! Print result
    for e in completeListOrdered.items():
        parent = e[1]["parent"]
        if parent is -1:
            print("Is root element id: ", e[0])
            nestedList[e[0]] = e
            #del completeListOrdered[e[0]]
    print("")
    print("Restructuring done!")
    print("Old structure:")
    for e in completeListOrdered.items():
        print(e)

    print("")
    print("New structure:")
    for e in nestedList.items():
        print(e)

    return nestedList



"""
    Finds Z values on the elements found in the picture
"""
def findZValues(listToFindZValues):
    print(len(listToFindZValues))

    for i in range(len(listToFindZValues)):
        zNumber = 0
        parent = ""
        for j in range(len(listToFindZValues)):
            tempOject = listToFindZValues[i]
            if(i != j):
                checkObject = listToFindZValues[j]

                tempOject1 = tempOject[1]
                tempOject2 = tempOject[2]
                tempOject3 = tempOject[3]
                tempOject4 = tempOject[4]

                checkObject1 = checkObject[1]
                checkObject2 = checkObject[2]
                checkObject3 = checkObject[3]
                checkObject4 = checkObject[4]

                if(tempOject1[1] >= checkObject1[1] and tempOject1[0] >= checkObject1[0] and tempOject2[1] <= checkObject2[1] and tempOject2[0] >= checkObject2[0] and tempOject3[1] >= checkObject3[1] and tempOject3[0] <= checkObject3[0] and tempOject4[1] <= checkObject4[1] and tempOject4[0] <= checkObject4[0]):
                    #zNumber += 1
                    parent = checkObject[5]

        #tempOject.append(zNumber)
        tempOject.append(parent)

    #print(listToFindZValues)
    return listToFindZValues


"""
    Takes the different boxes, one at a time and creates a JSON objects. Then it saves it to a file
"""
def JSONMakerAndSaver(ListToSaveJSONObjects, elements, completeList, completeListOrdered):
    data = {}
    data2 = OrderedDict()
    data2['id'] = int(elements[5])
    try:
        data2['parent'] = int(elements[6])
    except:
        data2['parent'] = -1     
    data2['color'] = elements[0]
    data2['x'] = elements[1][1]
    data2['y'] = elements[1][0]
    data2["width"] = elements[2][1] - elements[1][1]
    data2["height"] = elements[3][0] - elements[1][0]
    data2["content"] = OrderedDict()

    #print("DATA: ", data2)
    completeList.append(data2)
    #if 
    completeListOrdered[elements[5]] = data2
    #print("COMPLETE list: ", completeList)
    #print("Element: ", elements)
    
    hexValue = elements[0]
    data['content'] = "Color code: " + hexValue
    data['color'] = hexValue
    data['type'] = getType(hexValue, 0)
    data['y'] = elements[1][0]
    data['x'] = elements[1][1]
    data['width'] = elements[2][1] - elements[1][1]
    data['height'] = elements[3][0] - elements[1][0]
    data['ID'] = elements[5]
    data['PARENT'] = elements[6]
    ListToSaveJSONObjects.append(data)
    
    return ListToSaveJSONObjects

def WriteToFile(ListToSaveJSONObjects, outputPath, completeList):
    print("Unordered list: ", ListToSaveJSONObjects)
    #newList = listToOrderedList(ListToSaveJSONObjects)
    #print("Ordered list: ", newList)
    #data3 = OrderedDict(sorted(ListToSaveJSONObjects.items(), key=lambda t: ListToSaveJSONObjects[0]["ID"]))
    #print(data3)
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    f = open(outputPath+"/imageRepresentation.json", "w+")
    #json.dump(ListToSaveJSONObjects, f, sort_keys=False)
    #for (k,v) in completeList.items():
    #    print(v)
    #    json.dump(v.items(), f)
#    json.dump(completeList.items(), f, sort_keys=True)
    
    json.dump(completeList, f)


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
