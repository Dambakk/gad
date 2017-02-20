#!/usr/local/bin/env python3
import os
import argparse
from colorama import Fore, Back, Style
from distutils.dir_util import copy_tree
import re
import fileinput
from colorama import Fore, Back, Style
from collections import OrderedDict
import json
import configparser
from shutil import copy

listenM = {}
listenMP = {}
listenH = {}

def copyProject(outputPath, debug, args):
	newListeM = []
	newListeH = []
	newListeMP = []
	configSetup()
	if(os.path.exists(outputPath)):

		# Finner ID'ene i ny og gammel JSON
		newJSON, newJSONList = findIDJSON(args.jsonPath)
		print(newJSON, " test")

		oldJSONPath = outputPath+ "/exampleStructure1.json"
		oldJSON, oldJSONList = findIDJSON(oldJSONPath)
		print(oldJSON, " test1")

		# Lager en liste med ID'er som er annerledes, blir flere hvis det er flere her, blir tom hvis ikke.
		finalJSONID = []
		for i in newJSON:
			if(i not in oldJSON):
				 finalJSONID.append(i)

		print(finalJSONID)

		# Henter ut en flat struktur, så hvert JSON object kan hentes ut fra en liste, så man slipper reqursion for å hente ut.
		newFlatJSONList = []
		for x in newJSONList.items():
			readElementForNewListe(x[1][1], newFlatJSONList)

		# Gjør samme med gammel JSON struktur
		oldFlatJSONList = []
		for y in oldJSONList.items():
			readElementForNewListe(y[1][1], oldFlatJSONList)

		#Funksjon for å sjekke om vi har riktige ID'er
		checkIfCorrectID(newFlatJSONList, oldFlatJSONList, finalJSONID)

		print(newFlatJSONList)

	else:

		fromDirectory = "DemoApp"
		copy_tree(fromDirectory, outputPath)
		viewName = input("Enter a name for the new view: ")
		os.rename(outputPath + "/DemoApp/ViewControllerBase.h", outputPath + "/DemoApp/" + viewName + "Base.h")
		os.rename(outputPath + "/DemoApp/ViewControllerBase.m", outputPath + "/DemoApp/" + viewName + "Base.m")
		os.rename(outputPath + "/DemoApp/ViewController.m", outputPath + "/DemoApp/" + viewName + ".m")
		os.rename(outputPath + "/DemoApp/ViewController.h", outputPath + "/DemoApp/" + viewName + ".h")
		with open(args.jsonPath) as data_file:
		  data = OrderedDict()
		  try:
			data = json.load(data_file, object_pairs_hook=OrderedDict)
		  except ValueError:
			print(Fore.RED + "Something went wrong. Could not read JSON. Is the JSON structure correct?" + Style.RESET_ALL)
			return

		  for e in data.items():
			if e[0] != "meta":
			  readElement(e[1][1], newListeM, newListeH, newListeMP)
		if debug: print("Done parsing the JSON elements")
		replaceText(outputPath, "m", viewName, newListeM, newListeMP)
		replaceText(outputPath, "h", viewName, newListeH, None)  

	print(Fore.GREEN + "iOS generator done" + Fore.RESET)



def checkIfCorrectID(newJSON, oldJSON, finalJSONID):

	for i in newJSON:
		tempListe = []
		for j in oldJSON:

			if(i[1] == j[1] and i[2] == j[2] and i[3] == j[3] and i[4] == j[4] and i[5] == j[5]):
				i[0] = j[0]
				oldJSON.remove(j)
				break
			elif(i[1] == j[1]):
				tempListe.append(j)

		if tempListe:
			match = percentageMatch(tempListe, i)
			i[0] = match[0]
			oldJSON.remove(match)
		elif finalJSONID:
			print("We came here")
			i[0] = finalJSONID.pop(0)


		print(tempListe)

def percentageMatch(tempListe, elementToCheck):
	NUMBER = 200
	TRESHOLD = 0.1
	for currentElement in tempListe:
		percentage = abs((currentElement[2]-elementToCheck[2])/NUMBER) + abs((currentElement[3]-elementToCheck[3])/NUMBER) + abs((currentElement[4]-elementToCheck[4])/NUMBER) + abs((currentElement[5]-elementToCheck[5])/NUMBER)
		currentElement.append(percentage)
		print(currentElement)

	tempListe.sort(key=lambda x: x[8])

	print(tempListe)

	if(tempListe[0][8] < TRESHOLD):
		del tempListe[0][-1]
		print(tempListe[0])
		return tempListe[0]
	else:
		return None


def findIDJSON(filepath):
	test = []
	newData = []
	with open(filepath) as data_file:
		data = OrderedDict()
		try:
			data = json.load(data_file, object_pairs_hook=OrderedDict)
		except ValueError:
			print(Fore.RED + "Something went wrong. Could not read JSON. Is the JSON structure correct?" + Style.RESET_ALL)
			return

		for e in data.items():
			readElementForID(e[1][1], test)


	return test, data

def configSetup():
	Config = configparser.RawConfigParser()
	Config.read("colorTypes.ini")
	readConfigFile(Config)

def readConfigFile(config):
	options1 = config.options("implementationsFields")
	for option in options1:
		listenM["#" + option] = eval(config.get("implementationsFields", option))

	options2 = config.options("addingFields")
	for option in options2:
		if str(option) == 'default':
			listenMP[option] = eval(config.get("addingFields", option))
		else:
			listenMP["#" + option] = eval(config.get("addingFields", option))
	options3 = config.options("headerFields")
	for option in options3:
		listenH["#" + option] = eval(config.get("headerFields", option))


#Return (red, green, blue) for the color given as #rrggbb.
def hex_to_rgb(value):
	value = value.lstrip('#')
	lv = len(value)
	return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def saveIOSobjectM(color, elementId, posX, posY, width, height, liste, newListeM):
	if(color in liste):
		name = liste[color][0][0] + str(elementId)
		newItem = ""
		for i in range(1, len(liste[color])):
			item = liste[color][i]
			if ("NAME" in item[0]):
				newItem = str(item[0]).replace("NAME", str(name))
			if ("POSX" in item[0]):
				newItem = str(newItem).replace("POSX", str(posX))
			if ("POSY" in item[0]):
				newItem = str(newItem).replace("POSY", str(posY))
			if ("WIDTH" in item[0]):
				newItem = str(newItem).replace("WIDTH", str(width))
			if ("HEIGHT" in item[0]):
				newItem = str(newItem).replace("HEIGHT", str(height))
			if ("COLOR" in item[0]):
				(r,g,b) = hex_to_rgb(color)
				rgbColor = "colorWithRed:{0}/255.0 green:{1}/255.0 blue:{2}/255.0 alpha:1".format(r,g,b)
				newItem = str(newItem).replace("COLOR", rgbColor)
			newListeM.append(newItem)
	else:
		print(Fore.RED + color + " - is not a valid color and will be ignored" + Style.RESET_ALL
			+"\nRead the documentation to add your own colors and corresponding elements.")

def saveIOSobjectH(color, elementId, listenH, newListeH):
	if(color in listenH):
		name = listenH[color][0][0] + str(elementId)
		headerElement = listenH[color][1][0]
		newItem = str(headerElement).replace("NAME", str(name))
		newListeH.append(newItem)

def saveIOSobjectMP(newListeMP, parentColor, elementId, parent, listenMP, color):
	if(parent != -1):
		if(color in listenMP):
			name = listenM[color][0][0] + str(elementId)
			item = listenMP[parentColor][0]
			newItem = ""
			if("ID" in item[0]):
				newItem = str(item[0]).replace("ID", str(parent))
			if("NAME" in item[0]):
				newItem = str(newItem).replace("NAME", str(name))
			newListeMP.append(newItem)
	else:
		if(color in listenMP):
			item = listenMP['default'][0]
			name = listenM[color][0][0] + str(elementId)
			newItem = ""
			if("NAME" in item[0]):
				newItem = str(item[0]).replace("NAME", str(name))
			newListeMP.append(newItem)

def readElementForNewListe(element, newListe):
		elementId = element['id']
		contentStructure = element["content"]
		color = element["color"]
		posX = element["x"]
		posY = element["y"]
		width = element["width"]
		height = element["height"]
		parent = element["parent"]
		parentColor = element['parentColor']
		content = "Lorem"

		newListe.append([elementId, color, posX, posY, width, height, parent, parentColor])

		if len(contentStructure) > 0:
			for i in range (0, len(contentStructure)):
				content = readElementForNewListe(contentStructure[str(i)][1], newListe)


def readElementForID(element, test):
		elementId = element['id']
		test.append(elementId)
		contentStructure = element["content"]
		content = "Lorem"

		if len(contentStructure) > 0:
			for i in range (0, len(contentStructure)):
				content = readElementForID(contentStructure[str(i)][1], test)

def readElement(element, newListeM, newListeH, newListeMP):
	elementId = element['id']
	color = element["color"]
	posX = element["x"]
	posY = element["y"]
	width = element["width"]
	height = element["height"]
	parent = element["parent"]
	parentColor = element['parentColor']
	contentStructure = element["content"]

	saveIOSobjectM(color, elementId, posX, posY, width, height, listenM, newListeM)
	saveIOSobjectH(color, elementId,listenH, newListeH)
	saveIOSobjectMP(newListeMP, parentColor, elementId, parent, listenMP, color)

	if len(contentStructure) > 0:
		for i in range (0, len(contentStructure)):
			readElement(contentStructure[str(i)][1], newListeM, newListeH, newListeMP)
	  

def replaceText(templatePath, fileType, filename, elements, elements2):
	templatePath = templatePath+"/DemoApp"
	file1 = open(templatePath + "/" + filename + "Base." + fileType , "r")
	file2 = open(templatePath + "/NewFile.txt", "w")


	for line in file1:
		matchObj = re.match('\{\{\[\]\}\}', line)
		if(matchObj):
			file2.write("/* Declearing elements */\n")
			for i in elements:
				file2.write(i + "\n")
			if(elements2 != None):
				file2.write("\n")
				file2.write("/* Adding elements */\n")
				for j in elements2:
					file2.write(j + "\n")
		else:
			file2.write(line)
	file1.close()
	file2.close()

	file3 = open(templatePath + "/" + filename + "Base." + fileType , "w")
	file4 = open(templatePath + "/NewFile.txt", "r")

	for line in file4:
		file3.write(line)

	file3.close()
	file4.close()

	if(os.path.exists(templatePath + '/NewFile.txt')):
		os.remove(templatePath + '/NewFile.txt')

if __name__== "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("jsonPath", help="Path to JSON structure") #NB! Vi kan også bruke styles her! :)
	ap.add_argument("outputPath", help="Output directory")
	ap.add_argument("-v", "--verbose", help="Verbose output", action="store_true", default=False)
	args = ap.parse_args()
	
	copyProject(args.outputPath, args.verbose, args)
