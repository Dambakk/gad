#!/usr/local/bin/env python3
import os
import argparse
import json
from PIL import Image, ImageFilter
from colorama import Fore, Back, Style
import configparser
import collections
from collections import OrderedDict
import time

"""
	Main parser function
"""
def parseImage(path, outputPath, debug):
	image = Image.open(path)
	width, height = image.size

	if debug : print(Fore.GREEN + "Image loaded successfully" + Style.RESET_ALL)

	CompleteRGBDict = PixelSearcher(height, width, image)



	if debug :
		print("Done reading image")


	print(CompleteRGBDict)
	internalList = createJSONObjects(CompleteRGBDict, outputPath, debug)

	unorderedList = findZValues(internalList)

	completeListOrdered = createOrderedJSONStructure(unorderedList)

	nestedList = fixNesting(completeListOrdered)

	pathToJSON = writeToFile(outputPath, nestedList, image)

	if debug :
		print("JSON structure created and saved to file")

	print("-"*15)
	print(Fore.GREEN + "Image parser: Done." + Style.RESET_ALL
		+"\nFound " + str(len(internalList)) + " elements."
		+"\nJSON is stored on this path: " + Fore.YELLOW + pathToJSON + Style.RESET_ALL)

	return pathToJSON


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
					CheckIfCorner(RGBCornerPixels, x, y, image, number, (r,g,b), zValue, idValue)
					'''CheckIfCornerOneLine(RGBCornerPixels, x, y, image, number, (r,g,b), zValue, idValue)'''
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
		except KeyError:
			RGBCornerPixels[value1,value2,value3] = [[x,y]]

	x1,x2,x3,x4 = image.getpixel((y+1, x))
	z1,z2,z3,z4 = image.getpixel((y, x-1))
	RGB3 = x1,x2,x3
	RGB4 = z1,z2,z3
	if(RGB != RGB3 and RGB != RGB4):
		RGBCornerPixels[value1,value2,value3].append([x,y])

	x5,x6,x7,x8 = image.getpixel((y, x+1))
	z5,z6,z7,z8 = image.getpixel((y-1, x))
	RGB5 = x5,x6,x7
	RGB6 = z5,z6,z7
	if(RGB != RGB5 and RGB != RGB6):
		RGBCornerPixels[value1,value2,value3].append([x,y])

	x9, x10, x11, x12 = image.getpixel((y+1, x))
	z9,z10,z11,z12 = image.getpixel((y, x+1))
	RGB7 = x9,x10,x11
	RGB8 = z9,z10,z11
	if(RGB != RGB7 and RGB != RGB8):
		RGBCornerPixels[value1,value2,value3].append([x,y])


def CheckIfCornerOneLine(RGBCornerPixelsOneLiner, x, y, image, number, RGB, zValue, idValue):
	value1,value2,value3 = RGB
	r,g,b,a = image.getpixel((y, x-1))
	c,d,e,f = image.getpixel((y-1, x))
	g,h,i,j = image.getpixel((y+1, x))
	RGB1 = r,g,b
	RGB2 = c,d,e
	RGB3 = g,h,i

	if(RGB != RGB1 and RGB != RGB2 and RGB != RGB3):
		try:
			RGBCornerPixelsOneLiner[value1,value2,value3].append([x,y])
			RGBCornerPixelsOneLiner[value1,value2,value3].append([x+1,y])
		except KeyError:
			RGBCornerPixelsOneLiner[value1,value2,value3] = [[x,y], [x+1, y]]

	x1,x2,x3,x4 = image.getpixel((y, x+1))
	z1,z2,z3,z4 = image.getpixel((y-1, x))
	x5,x6,x7,x8 = image.getpixel((y+1, x))
	RGB4 = x1,x2,x3
	RGB5 = z1,z2,z3
	RGB6 = x5,x6,x7
	if(RGB != RGB4 and RGB != RGB5 and RGB != RGB6):
		RGBCornerPixelsOneLiner[value1,value2,value3].append([x,y])
		RGBCornerPixelsOneLiner[value1,value2,value3].append([x+1,y])


	xx1,xx2,xx3,xx4 = image.getpixel((y, x+1))
	xx5,xx6,xx7,xx8 = image.getpixel((y, x-1))
	xx9,xx10,xx11,xx12 = image.getpixel((y-1, x))
	RGB7 = xx1,xx2,xx3
	RGB8 = xx5,xx6,xx7
	RGB9 = xx9,xx10,xx11
	if(RGB != RGB7 and RGB != RGB8 and RGB != RGB9):
		RGBCornerPixelsOneLiner[value1,value2,value3].append([x,y])
		RGBCornerPixelsOneLiner[value1,value2,value3].append([x,y+1])

	zz1,zz2,zz3,zz4 = image.getpixel((y, x+1))
	zz5,zz6,zz7,zz8 = image.getpixel((y, x-1))
	zz9,zz10,zz11,zz12 = image.getpixel((y+1, x))
	RGB10 = zz1,zz2,zz3
	RGB11 = zz5,zz6,zz7
	RGB12 = zz9,zz10,zz11
	if(RGB != RGB10 and RGB != RGB11 and RGB != RGB12):
		RGBCornerPixelsOneLiner[value1,value2,value3].append([x,y])
		RGBCornerPixelsOneLiner[value1,value2,value3].append([x,y+1])


def ConvertToHex(rgbColor):
	hexValue = '#%02x%02x%02x' % (rgbColor[0], rgbColor[1], rgbColor[2])
	return hexValue


def createJSONObjects(CompleteRGBDict, outputPath, debug=False):
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

	#Append different ID to all elements
	idNumber = 0
	for x in listToFindZValues:
		x.append(str(idNumber))
		idNumber += 1

	return listToFindZValues

"""
	Go throug list and move childs to content of parent and return
	the new, correctly nested list.
"""
def fixNesting(elementsOrdered):
	nestedList = OrderedDict()

	#Connect those with parents by move references around
	for e in elementsOrdered.items():
		parent = e[1]["parent"]
		if parent is not -1: #if not root element, move ref to content of parent
			size = len(elementsOrdered[str(parent)]["content"])
			e[1]['parentColor'] = elementsOrdered[str(parent)]["color"]
			elementsOrdered[str(parent)]["content"][size] = e

	#Move root elemets with nested elements to own list
	for e in elementsOrdered.items():
		parent = e[1]["parent"]
		if parent is -1:
			nestedList[e[0]] = e

	return nestedList


"""
	Finds Z values on the elements found in the picture
"""
def findZValues(listToFindZValues):

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
					parent = checkObject[5]

		tempOject.append(parent)

	return listToFindZValues



"""
	Takes an unordered list and creates an ordered list and returns this new list
"""
def createOrderedJSONStructure(unorderedList):
	completeListOrdered = OrderedDict()
	for element in unorderedList:
		data2 = OrderedDict()
		data2['id'] = int(element[5])
		try:
			data2['parent'] = int(element[6]) # add parent if any
		except:
			data2['parent'] = -1 # if not any parent, element is root element and parent is -1
		data2['parentColor'] = ""
		data2['color'] = element[0]
		data2['x'] = element[1][1]
		data2['y'] = element[1][0]
		data2["width"] = element[2][1] - element[1][1]
		data2["height"] = element[3][0] - element[1][0]
		data2["content"] = OrderedDict()

		completeListOrdered[element[5]] = data2

	return completeListOrdered


"""
	Write the ordered list to file in a JSON structure
"""
def writeToFile(outputPath, completeList, image):
	filePath = outputPath+"/imageRepresentation.json"
	if not os.path.exists(outputPath):
		os.makedirs(outputPath)
	f = open(filePath, "w+")

	meta = OrderedDict()

	width, height = image.size
	meta["date"] = time.strftime("%d/%m/%Y")
	meta["imageWidth"] = width
	meta["imageHeight"] = height
	completeList["meta"] = meta

	json.dump(completeList, f)
	f.close()
	return filePath


"""
	Finds the four corners of the given box.
"""
def findTheSquares(corners, squaresList):
	while len(corners) != 0:
		firstCorner = corners[0]

		'''corners.pop(0)
		corners.pop(0)'''

		for i in range(len(corners-2)):
			secondCorner = corners[i+1]

			value1, value2 = findEndCorners(corners, firstCorner, secondCorner)

			if(value1 != -1 and value2 != -1):
				thirdCorner = corners[value1]
				fourthCorner = corners[value2]

				del corners[firstCorner:secondCorner]
				del corners[value1:value2+1]

				squaresList.append([firstCorner,secondCorner, thirdCorner, fourthCorner])

"""
	Helper function to find the end corners
"""

def findEndCorners(corners, firstCorner, secondCorner):
	firstValue = -1
	secondValue = -1
	number = 0

	for i in range(len(corners)-1):
		if(corners[i][1] == firstCorner[1] and corners[i+1][1] == secondCorner[1]):
			firstValue = number
			secondValue = number+1
		number += 1




	"""
	for i in corners:
		if(i[1] == firstCorner[1]):
			firstValue = number
		if(i[1] == secondCorner[1]):
			secondValue = number
			break
		number += 1
	"""

	return (firstValue,secondValue)




if __name__== "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("inputImage", help="Path to selected image")
	ap.add_argument("outputPath", help="Path to output directory")
	ap.add_argument("-v", "--verbose", help="Verbose output level", action="store_true", default=False)
	args = ap.parse_args()

	if not(args.inputImage.lower().endswith(".png")):
		print(Fore.RED + "File should be an image file (png)." + Style.RESET_ALL)
		print(Fore.RED + "Exiting..." + Style.RESET_ALL)
	else:
		imagePath = os.path.abspath(args.inputImage)
		outputPath = os.path.abspath(args.outputPath)
		parseImage(imagePath, outputPath, args.verbose)
