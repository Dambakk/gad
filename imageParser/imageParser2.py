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
from operator import itemgetter
from copy import deepcopy


"""
	Main parser function
"""
def parseImage(path, outputPath, debug):
	image = Image.open(path)
	width, height = image.size

	if debug : print(Fore.GREEN + "Image loaded successfully" + Style.RESET_ALL)

	''' Finds all corners in the image '''
	CompleteRGBDict = PixelSearcher(height, width, image)


	if debug : print("Done reading image")

	''' Creates the JSON objects without nesting and parents '''
	internalList = createJSONObjects(CompleteRGBDict,image ,debug )

	''' Finds the correct Z-values (parents) '''
	unorderedList = findZValues(internalList)

	''' Creates the correct ordered structure in JSON '''
	completeListOrdered = createOrderedJSONStructure(unorderedList, debug)

	''' Fixes the nested lists, changing the flat structure to the correct structure with nesting of child elements '''
	nestedList = fixNesting(completeListOrdered, debug)

	''' Writes the correct nested structure to the specified location '''
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
	Function that searchs through the image and saving corners as a list
"""
def PixelSearcher(height, width, image):

	RGBCornerPixels = {}
	for x in range(0, height):
		for y in range(0, width):
			r,g,b,a = image.getpixel((y, x))
			if (r != 255 or g != 255 or b != 255):
				if(x < height-1 and y < width-1 and x > 0 and y > 0):
					CheckIfCorner(RGBCornerPixels, x, y, image, (r,g,b))
				else:
					CheckIfCornerAtBorder(RGBCornerPixels, x, y, image, (r,g,b))
	return RGBCornerPixels

"""
	Function that checks if we have a corner. It checks the four possibilites - top left and right and bottom left and right
	Helper function to the PixelSearcher to check if the coords are a corner or not
"""
def CheckIfCorner(RGBCornerPixels, x,y, image, RGB):
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


"""
	Checks if it is a corner on the edge of the image - also a helper function to the PixelSearcher
"""
def CheckIfCornerAtBorder(RGBCornerPixels, x, y, image, RGB):
	value1,value2,value3 = RGB

	if(value1 != 255 or value2 != 255 or value3 != 255):
		try:
			RGBCornerPixels[value1,value2,value3].append([x,y])
		except KeyError:
			RGBCornerPixels[value1,value2,value3] = [[x,y]]


"""
	Function that converts the RGB value to a hexadecimal value
"""
def ConvertToHex(rgbColor):
	hexValue = '#%02x%02x%02x' % (rgbColor[0], rgbColor[1], rgbColor[2])
	return hexValue

"""
	Function that takes the complete dictionary with corners and matches the correct corners to the correct boxes
	Based on the boxes it creates the JSON objects with different ID's. Correct nesting and parenting is not fixed here,
	only the flat default structure is fixed here.
"""
def createJSONObjects(CompleteRGBDict, image,debug=False):
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
		findTheSquares(num2, squaresList, rgbColor, image)
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
def fixNesting(elementsOrdered, debug):
	#tempList = deepcopy(elementsOrdered)
	nestedList = OrderedDict()

	#Connect those with parents by move references around
	for e in elementsOrdered.items():
		parent = e[1]["parent"]
		if parent is not -1: #if not root element, move ref to content of parent
			size = len(elementsOrdered[str(parent)]["content"])
			e[1]['parentColor'] = elementsOrdered[str(parent)]["color"]

			#Add relative coordinates:
			e[1]["relX"] = e[1]["x"] - elementsOrdered[str(parent)]["x"]
			e[1]["relY"] = e[1]["y"] - elementsOrdered[str(parent)]["y"]

			#Append element as child/content of parent:
			elementsOrdered[str(parent)]["content"][size] = e
		elif parent is -1:
			e[1]["relX"] = e[1]["x"]
			e[1]["relY"] = e[1]["y"]

	#Move root elemets with nested elements to own list
	for e in elementsOrdered.items():
		parent = e[1]["parent"]
		if parent is -1:
			nestedList[e[0]] = e

	return nestedList


"""
	Finds Z values on the elements found in the picture
	lambda to sort the list on the lowest x and y values - does the trick when checking for parents
"""
def findZValues(listToFindZValues):

	listToFindZValues.sort(key = lambda element: (element[1], -element[2][1]))

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
def createOrderedJSONStructure(unorderedList, debug):
	completeListOrdered = OrderedDict()
	if debug: print(Fore.BLUE + "Found following elements:"+Style.RESET_ALL)
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
		data2['relX'] = -1
		data2['relY'] = -1
		data2["width"] = element[2][1] - element[1][1]
		data2["height"] = element[3][0] - element[1][0]
		data2["content"] = OrderedDict()

		completeListOrdered[element[5]] = data2
		if debug: print('*	element id:', data2['id'], '	parent id:', data2['parent'], '		(x,y): (', data2['x'], ',' ,data2['y'], ') 	(w,h): (', data2['width'], ',', data2['height'], ')	 color: ', data2['color'] )


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

	json.dump(completeList, f, indent=4)
	f.close()
	return filePath


"""
	Goes through all the elements in the different colors and maps the correct corners to find the correct boxes
	Helper function to the createJSONObjects.
"""
def findTheSquares(corners, squaresList, rgbColor, image):

	''' Removes duplicate entries when hairlines is present '''
	corners = [list(x) for x in set(tuple(x) for x in corners)]
	corners.sort(key = lambda element: (element))

	while len(corners) != 0:
		firstCorner = corners[0]

		try:
			a,b,c,d = image.getpixel((firstCorner[1], firstCorner[0]-1))
			e,f,g,h = image.getpixel((firstCorner[1], firstCorner[0]+1))
			firstColor = a,b,c
			secondColor = e,f,g
		except:
			firstColor = None
			secondColor = None
		try:
			x,y,z,w = image.getpixel((firstCorner[1]-1, firstCorner[0]))
			x1,y1,z1,w1 = image.getpixel((firstCorner[1]+1, firstCorner[0]))
			thirdColor = x,y,z
			fourthColor = x1,y1,z1
		except:
			thirdColor = None
			fourthColor = None

		''' Checks if it is a hairline - handeled different '''
		if((firstColor != rgbColor and secondColor != rgbColor and firstColor != None and secondColor != None) or (thirdColor != rgbColor and fourthColor != rgbColor and thirdColor != None and fourthColor != None)):
			minX, minY, maxX, maxY = findMaxAndMinHairLine(firstCorner, corners, rgbColor, image, firstColor, secondColor)

		else:
			minX, minY, maxX, maxY = findMaximumAndMinimumValues(corners, firstCorner, rgbColor, image)

		corners.pop(0)
		#if(minX == maxX):
		#	maxX += 1
		squaresList.append([[minY, minX], [minY, maxX], [maxY, minX], [maxY, maxX]])


"""
		Follows the hairline pixels, then gives the correct widht/height back.
		Helper function to findTheSquares - special case hairline.
"""
def findMaxAndMinHairLine(firstCorner, corners, rgbColor, image, firstColor, secondColor):

	minX = firstCorner[1]
	maxX = firstCorner[1]+1
	minY = firstCorner[0]
	maxY = firstCorner[0]+1

	a,b,c = rgbColor
	d = 255
	newColor = a,b,c,d

	if(firstColor != rgbColor and secondColor != rgbColor):
		while(image.getpixel((maxX, firstCorner[0])) == newColor):
			testValue = [firstCorner[0], maxX]
			for value in corners:
				if(testValue == value):
					corners.remove(value)
			maxX += 1
		return minX, minY, maxX, maxY
	else:

		while(image.getpixel((firstCorner[1], maxY)) == newColor):
			testValue = [maxY, firstCorner[1]]
			for value in corners:
				if(testValue == value):
					corners.remove(value)
			maxY += 1
		return minX, minY, maxX, maxY


"""
	Helper function to find the corners (findTheSquares)
	Searches "around" the box to find the correct maximum and minimum values, the loop function
	returns the max and minimum x and y values
"""
def findMaximumAndMinimumValues(corners, firstCorner, rgbColor, image):
	a,b,c = rgbColor
	rgbColor = a,b,c,255

	xValue = -1
	yValue = -1
	minX = firstCorner[1]
	minY = firstCorner[0]
	maxX = firstCorner[1]
	maxY = firstCorner[0]

	width, height = image.size

	if(image.getpixel((firstCorner[1], firstCorner[0])) == rgbColor and (firstCorner[0] == 0 or firstCorner[1] == 0)):
		xValue = firstCorner[1]+1
		yValue = firstCorner[0]

	if(firstCorner[1] != width-1 and firstCorner[1] != 0 and firstCorner[0] != 0 and firstCorner[0] != height-1):
		if(image.getpixel((firstCorner[1]+1, firstCorner[0])) == rgbColor and image.getpixel((firstCorner[1]+1, firstCorner[0]-1)) != rgbColor):
			xValue = firstCorner[1]+1
			yValue = firstCorner[0]
			maxX += 1


	while(xValue != firstCorner[1] or yValue != firstCorner[0]):
		testValue = [yValue, xValue]
		for value in corners:
			if(testValue == value):
				corners.remove(value)

		if(xValue == width-1 or yValue == height-1 or xValue == 0 or yValue == 0):
			if((yValue == 0 and xValue < width-1 and image.getpixel((xValue+1, yValue)) == rgbColor) or (yValue != 0 and xValue == 0 and image.getpixel((xValue, yValue-1)) != rgbColor)):
				xValue = xValue+1
				if(xValue > maxX):
					maxX = xValue

			elif(xValue != 0 and yValue < height-1 and image.getpixel((xValue, yValue+1)) == rgbColor):
				yValue = yValue+1
				if(yValue > maxY):
					maxY = yValue

			elif(xValue > 0 and image.getpixel((xValue-1, yValue)) == rgbColor):
				xValue = xValue-1
				if(xValue < minX):
					minX = xValue

			elif(image.getpixel((xValue, yValue-1)) == rgbColor):
				yValue = yValue-1

		else:
			if((image.getpixel((xValue+1, yValue)) == rgbColor and image.getpixel((xValue+1, yValue-1)) != rgbColor) or (image.getpixel((xValue+1, yValue+1)) == rgbColor and image.getpixel((xValue+1, yValue)) != rgbColor)):
				xValue = xValue+1
				if(xValue > maxX):
					maxX = xValue

			elif((image.getpixel((xValue-1, yValue)) == rgbColor and image.getpixel((xValue, yValue+1)) != rgbColor) or image.getpixel((xValue-1, yValue-1)) == rgbColor and image.getpixel((xValue-1, yValue)) != rgbColor):
				xValue = xValue-1
				if(xValue < minX):
					minX = xValue

			elif(image.getpixel((xValue, yValue+1)) == rgbColor and image.getpixel((xValue+1, yValue+1)) != rgbColor):
				yValue = yValue+1
				if(yValue > maxY):
					maxY = yValue

			elif((image.getpixel((xValue, yValue-1)) == rgbColor and image.getpixel((xValue-1, yValue-1)) != rgbColor) or (image.getpixel((xValue+1, yValue-1)) == rgbColor and image.getpixel((xValue, yValue-1)) != rgbColor)):
				yValue = yValue-1

	return minX, minY, maxX, maxY



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
