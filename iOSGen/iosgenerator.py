#!/usr/local/bin/env python3
import os
import argparse
from colorama import Fore, Back, Style
from distutils.dir_util import copy_tree
import re
from colorama import Fore, Back, Style
from collections import OrderedDict
import json
import configparser
from shutil import copy
import shutil
from pprint import pprint
import glob
import time
import subprocess
import readline
import rlcompleter
from git import *
import sys

listenM = {}
listenMP = {}
listenH = {}

OUTPUTPATH = ""
VIEWS = []
usingGit = False

"""
	Main function
"""
def initProject(outputPath, debug, args, appName):
	global VIEWS

	'''Read config file'''
	configSetup()
	if debug: print("Config file loaded")

	print("-"*20)

	'''Checks if the project exists and checks whether a view should be changed or a new one added'''
	if(os.path.exists(outputPath)):
		if debug: print("Project already exists...")
		VIEWS = [f for f in os.listdir(outputPath + "/" + appName + "/") if re.match("[a-zA-Z0-9]*Base.h", f)]
		#Check that all project files exists.

		print(Fore.CYAN + "Project already exists on current path." + Style.RESET_ALL +
			"\nDo you want to update an existing view (1) or add a new view (2)?")
		res = input("Enter 1 or 2: ")
		while res not in {"1", "2"}:
			print(Fore.RED + "You entered something invalid." + Style.RESET_ALL + " Try again.")
			res = input("Enter 1 or 2: ")

		if res == "1": # UPDATE AN EXISTING VIEW
			print("Update a view selected...")

			fileToBeChanged = selectViewFile(outputPath, appName, debug)

			print(Fore.GREEN + "All good so far! " + Style.RESET_ALL + " File to be changed: " + Fore.CYAN + fileToBeChanged + Style.RESET_ALL)


			'''Find the new IDs when comparing the old and new JSON'''
			newJSON, newJSONList, newMeta = findIDJSON(args.jsonPath)

			oldJSONPath = outputPath+ "/json/" + fileToBeChanged[:-4] + ".json"
			oldJSON, oldJSONList, oldMeta = findIDJSON(oldJSONPath)


			'''Check for same image size and other requirements (e.g. that all project files are present...)'''
			if oldMeta["imageWidth"] != newMeta["imageWidth"] or oldMeta["imageHeight"] != newMeta["imageHeight"]:
				if args.force:
					print(Fore.RED + "Warning! " + Fore.YELLOW + "The old and new image has not the same size."
						+"\nThis may result in some unexpected behavior and results. You added 'force' and we will continue." + Style.RESET_ALL)
				else:
					print(Fore.RED+"The old and new image has not same width and heigth. This is a requirement."
						+"\nSee the documentation for more information."
						+Fore.YELLOW+"\nIf you still want to continue, run the same command with '--force' on the end."
						+Fore.RED+"\nExiting..."+ Style.RESET_ALL)
					sys.exit("ERROR: Incompatible image sizes.")



			'''Making a list with the new IDs'''
			finalJSONID = []
			for i in newJSON:
				if(i not in oldJSON):
					 finalJSONID.append(i)

			'''Saving JSON objects as a flat structure for new JSON structure'''
			newFlatJSONList = []
			for x in newJSONList.items():
				if x[0] != "meta":
					readElementForNewListe(x[1][1], newFlatJSONList)

			'''Saving JSON objects as a flat structure for old JSON structure'''
			oldFlatJSONList = []
			for y in oldJSONList.items():
				if y[0] != "meta":
					readElementForNewListe(y[1][1], oldFlatJSONList)

			'Checks if the IDs are correct. The update view function'

			checkIfCorrectID(newFlatJSONList, oldFlatJSONList, finalJSONID, args.threshold, oldMeta["imageWidth"], oldMeta["imageHeight"])

			'Update the JSON file saved to be the new structure genrated'
			updatedJSON = regenerateJSON(newFlatJSONList)


			'Copy a new view, which is going to be the updated to new dest'
			copy("DemoApp/DemoApp/ViewControllerBase.m", outputPath + "/" + appName + "/")
			copy("DemoApp/DemoApp/ViewControllerBase.h", outputPath + "/" + appName + "/")
			copy("DemoApp/DemoApp/ViewController.m", outputPath + "/" + appName + "/")
			copy("DemoApp/DemoApp/ViewController.h", outputPath + "/" + appName + "/")

			testerViewName = fileToBeChanged[:-4]


			os.remove(outputPath + "/" + appName + "/" + fileToBeChanged + ".h")
			os.remove(outputPath + "/" + appName + "/" + fileToBeChanged + ".m")
			os.remove(outputPath + "/" + appName + "/" + fileToBeChanged[:-4] + ".h")
			os.remove(outputPath + "/" + appName + "/" + fileToBeChanged[:-4] + ".m")

			os.rename(outputPath + "/" + appName + "/ViewControllerBase.m", outputPath + "/" + appName + "/" + fileToBeChanged + ".m")
			os.rename(outputPath + "/" + appName + "/ViewControllerBase.h", outputPath + "/" + appName + "/" + fileToBeChanged + ".h")
			os.rename(outputPath + "/" + appName + "/ViewController.m", outputPath + "/" + appName + "/" + fileToBeChanged[:-4] + ".m")
			os.rename(outputPath + "/" + appName + "/ViewController.h", outputPath + "/" + appName + "/" + fileToBeChanged[:-4] + ".h")

			prepareFiles(outputPath, fileToBeChanged[:-4], "m", appName)
			prepareFiles(outputPath, fileToBeChanged[:-4], "h", appName)


			iterateJSONAndGenerateCode(updatedJSON, outputPath, testerViewName, appName, debug)

			writeJSONToFile(outputPath, updatedJSON, newMeta, fileToBeChanged[:-4])

			#Checks if it is a git repo
			if isGitRepo(outputPath):
				print(Fore.YELLOW + "Detects a git repo!" + Style.RESET_ALL)
				a = input( "Do you want to commit the changes? (Y/N) ")
				while a not in {"Y", "N"} : a = input( "Do you want to commit the changes? (Y/N) ")
				if a is "Y":
					git = Git(os.path.abspath(outputPath))
					git.add("-A") #Add all
					git.commit("-m", "Changed a view: " + fileToBeChanged[:-4])
					print(Fore.GREEN + "Commited the changes" + Style.RESET_ALL)
					print(Fore.YELLOW + "Commit short hash: \t" + Style.RESET_ALL + git.log("--pretty=format:'%h'", "-n", 1))
					print(Fore.YELLOW + "Commit message:    \t" + Style.RESET_ALL + git.log(-1, "--pretty=%B")) #show last commit message
				else:
					print("No commit. Continuing...")

		elif res == "2":
			print("Adding view to the existing project...")
			viewName = input("Enter a name for the new view: ")

			#Copy new view to new dest
			copy("DemoApp/DemoApp/ViewControllerBase.m", outputPath + "/" + appName + "/")
			copy("DemoApp/DemoApp/ViewControllerBase.h", outputPath + "/" + appName + "/")
			copy("DemoApp/DemoApp/ViewController.m", outputPath + "/" + appName + "/")
			copy("DemoApp/DemoApp/ViewController.h", outputPath + "/" + appName + "/")

			os.rename(outputPath + "/" + appName + "/ViewControllerBase.h", outputPath + "/" + appName + "/" + viewName + "Base.h")
			os.rename(outputPath + "/" + appName + "/ViewControllerBase.m", outputPath + "/" + appName + "/" + viewName + "Base.m")
			os.rename(outputPath + "/" + appName + "/ViewController.m", outputPath + "/" + appName + "/" + viewName + ".m")
			os.rename(outputPath + "/" + appName + "/ViewController.h", outputPath + "/" + appName + "/" + viewName + ".h")

			prepareFiles(outputPath, viewName, "m", appName)
			prepareFiles(outputPath, viewName, "h", appName)

			with open(args.jsonPath) as data_file:
				data = OrderedDict()
				try:
					data = json.load(data_file, object_pairs_hook=OrderedDict)
				except ValueError:
					print(Fore.RED + "Something went wrong. Could not read JSON. Is the JSON structure correct?" + Style.RESET_ALL)
					return
				#Generates the code from the given JSON structure
				iterateJSONAndGenerateCode(data, outputPath, viewName, appName, debug)

				'Writes the JSON to a file, so a view can be updated later'
				writeJSONToFile(outputPath, data, data["meta"], viewName)

			#Is a git repo?
			if isGitRepo(outputPath):
				print(Fore.YELLOW + "Detects a git repo!" + Style.RESET_ALL)
				a = input( "Do you want to commit the changes? (Y/N) ")
				while a not in {"Y", "N"} : a = input( "Do you want to commit the changes? (Y/N) ")
				if a is "Y":
					git = Git(os.path.abspath(outputPath))
					git.add("-A") #Add all
					git.commit("-m", "Added a new view: " + viewName)
					print(Fore.GREEN + "Commited the changes" + Style.RESET_ALL)
					print(Fore.YELLOW + "Commit short hash: \t" + Style.RESET_ALL + git.log("--pretty=format:'%h'", "-n", 1))
					print(Fore.YELLOW + "Commit message:    \t" + Style.RESET_ALL + git.log(-1, "--pretty=%B")) #show last commit message
				else:
					print("No commit. Continuing...")

	else:
		print("Creating a new app...")
		print("OutputPath: " + outputPath)
		print("AppName: " + appName)

		#Copies the template project
		copy_tree("DemoApp", outputPath)
		answer = input("Do you want to initalize this app with git? (Y/N): ")
		while answer not in {"Y", "N"} : answer = input("Do you want to initalize this app with git? (Y/N): ")
		usingGit = False
		if answer is "Y":
			print(Fore.GREEN + "Git it is!" + Style.RESET_ALL)
			usingGit = True
			git = Git(os.path.abspath(outputPath))
			git.init()
			if debug: print("Initialized git repository")
		viewName = input("Enter a name for the new view: ")

		#TODO: Add some form of checking on the name for any invalid input?

		#Replacs all the old appname with the new appname
		searchReplaceInAllFoldersAndFiles(outputPath, "DemoApp", appName, (".txt", ".pbxproj", "DemoAppTests.m", "DemoAppUITests.m", "contents.xcworkspacedata", "AppDelegate.m"))
		searchReplaceInAllFoldersAndFiles(outputPath, "viewname", viewName, ("AppDelegate.m"))
		renameFilesAndFolders(outputPath, "DemoApp", outputPath, appName)

		os.rename(outputPath + "/" + appName + "/ViewControllerBase.h", outputPath + "/" + appName + "/" + viewName + "Base.h")
		os.rename(outputPath + "/" + appName + "/ViewControllerBase.m", outputPath + "/" + appName + "/" + viewName + "Base.m")
		os.rename(outputPath + "/" + appName + "/ViewController.m", outputPath + "/" + appName + "/" + viewName + ".m")
		os.rename(outputPath + "/" + appName + "/ViewController.h", outputPath + "/" + appName + "/" + viewName + ".h")

		os.remove(outputPath + "/json/asdfghjkl.json")

		prepareFiles(outputPath, viewName, "m", appName)
		prepareFiles(outputPath, viewName, "h", appName)

		#Reads the JOSN and generates the Code
		with open(args.jsonPath) as data_file:
			data = OrderedDict()
			try:
				data = json.load(data_file, object_pairs_hook=OrderedDict)
			except ValueError:
				print(Fore.RED + "Something went wrong. Could not read JSON. Is the JSON structure correct?" + Style.RESET_ALL)
				return
			iterateJSONAndGenerateCode(data, outputPath, viewName, appName, debug)

			writeJSONToFile(outputPath, data, data["meta"], viewName)

		#Add git functionality
		if usingGit:
			git = Git(os.path.abspath(outputPath))
			git.add("-A") #Add all
			git.commit("-m", "Initial commit. Added project files and first view: " + viewName)
			print(Fore.GREEN + "Commited the project" + Style.RESET_ALL)
			print(Fore.YELLOW + "Commit short hash: \t" + Style.RESET_ALL + git.log("--pretty=format:'%h'", "-n", 1))
			print(Fore.YELLOW + "Commit message:    \t" + Style.RESET_ALL + git.log(-1, "--pretty=%B")) #show last commit message

	print(Fore.GREEN + "iOS generator done" + Fore.RESET)
"""
	Tab completion
"""
def completer(text, state):
	files = [f[:-2] for f in VIEWS if f.startswith(text)]
	if state < len(files):
		return files[state]
	else:
		return None

"""
	Regenerates the flat JSON structure back to the nested version
"""
def regenerateJSON(oldList):
	#Create a flat, ordered structure
	newFlatJson = OrderedDict()
	for element in oldList:
		data = OrderedDict()
		data['id'] = element[0]
		data['parent'] = element[8]
		data['parentColor'] = element[9]
		data['color'] = element[1]
		data['x'] = element[2]
		data['y'] = element[3]
		data['relX'] = element[4]
		data['relY'] = element[5]
		data["width"] = element[6]
		data["height"] = element[7]
		data["content"] = OrderedDict()

		newFlatJson[element[0]] = data

	#Recreate the nested structure
	nestedList = OrderedDict()

	#Connect those with parents by move references around
	for e in newFlatJson.items():
		parent = e[1]["parent"]
		if parent is not -1: #if not root element, move ref to content of parent
			size = len(newFlatJson[parent]["content"])
			e[1]['parentColor'] = newFlatJson[parent]["color"]
			newFlatJson[parent]["content"][size] = e

	#Move root elemets with nested elements to own list
	for e in newFlatJson.items():
		parent = e[1]["parent"]
		if parent is -1:
			nestedList[e[0]] = e

	return nestedList

"""
	Iterates the JSON and generates the code'
"""
def iterateJSONAndGenerateCode(data, outputPath, viewName, appName, debug):
	newListeM = []
	newListeH = []
	newListeMP = []

	for e in data.items():
		if e[0] != "meta":
			readElement(e[1][1], newListeM, newListeH, newListeMP)
	if debug: print("Done parsing the JSON elements")

	replaceText(outputPath, "m", viewName, newListeM, newListeMP, appName)
	replaceText(outputPath, "h", viewName, newListeH, None, appName)


"""
	Checks if it is a git repo
"""
def isGitRepo(path):
	g = Git(os.path.abspath(path))
	try:
		g.rev_parse("--is-inside-work-tree")
		return True
	except GitCommandError as e:
		return False
	return False


"""
	Iterate all files in given directory and all subdirectories and
	searches and replaces the searchterm in all files that matches
	the file pattern.
"""
def searchReplaceInAllFoldersAndFiles(root, find, replace, FilePattern):
	for path, dirs, files in os.walk(os.path.abspath(root)):
		for filename in files:
			if filename.endswith(FilePattern):
				filepath = os.path.join(path, filename)
				with open(filepath) as f:
					s = f.read()
				s = s.replace(find, replace)
				with open(filepath, "w") as f:
					f.write(s)


"""
	Start in a root folder and change the name of all files and
	subdirectories.
"""
def renameFilesAndFolders(root, find, replace, appName):
	for path, dirs, files in os.walk(os.path.abspath(root)):
		for dirNr in range(len(dirs)):
			dirOld = appName + "/" + dirs[dirNr]
			dirNew = dirs[dirNr].replace(find, appName)
			if dirNew is not dirs[dirNr]:
				shutil.move(os.path.join(path, dirs[dirNr]), os.path.join(path, dirNew))
				dirs[dirNr] = dirNew #Update the dir name in the original list
		for filename in files:
			filenameNew = filename.replace(find, appName)
			if filenameNew != filename:
				os.rename(os.path.join(path, filename), os.path.join(path, filenameNew))

"""
	Selects the view file, which is supposed to be changed
"""
def selectViewFile(outputPath, appName, debug):
	if 'libedit' in readline.__doc__:
		readline.parse_and_bind("bind ^I rl_complete")
	else:
		readline.parse_and_bind("tab: complete")
	readline.set_completer(completer)

	#Get the name of the view to be changed
	files = [f for f in os.listdir(outputPath + "/" + appName + "/") if re.match("[a-zA-Z0-9]*Base.h", f)]
	if len(files) == 1:
		fileToBeChanged = files[0]
		if debug: print("Found only one view meeting the requirements: " + fileToBeChanged[:-2])
	elif len(files) == 0:
		print(Fore.RED + "Error! " + Fore.YELLOW + "Did not find any views matching the requirements."
			+"\nSee the documentation for more information. Error code: xx" + Style.RESET_ALL)
		return
	else:
		print(Fore.CYAN + "All editable views in project:" + Style.RESET_ALL)
		for f in files:
			print(Fore.YELLOW + "--> " + Style.RESET_ALL + f[:-2])
		print("Write the name of the view you want to change: ")
		fileToBeChanged = input("File name: ") + ".h"
		while fileToBeChanged not in files:
			for f in files:
				print(Fore.YELLOW + "--> " + Style.RESET_ALL + f[:-2])
			print(Fore.RED + "Not a valid file name. "+ Style.RESET_ALL + "Try again. Enter file name: ")
			fileToBeChanged = input("Full file name: ") + ".h"

	return fileToBeChanged[:-2]

"""
	Write the ordered list to file in a JSON structure
"""
def writeJSONToFile(outputPath, completeList, meta, viewName):
	filePath = outputPath+"/json/"+viewName+".json"
	if not os.path.exists(outputPath):
		os.makedirs(outputPath)
	f = open(filePath, "w+")

	meta["date"] = time.strftime("%d/%m/%Y")

	completeList["meta"] = meta

	json.dump(completeList, f, indent=4)
	f.close()
	return filePath

"""
	Checks if the elements in the old and new JSON are the same.
"""
def checkIfCorrectID(newJSON, oldJSON, finalJSONID, threshold, widthMeta, heightMeta):
	threshold = threshold/100

	try:
		counter = max(finalJSONID)+1
	except:
		sortedList = newJSON[:]
		sortedList.sort(key = lambda element: (element[0]), reverse=True)
		counter = sortedList[0][0] + 1

	for i in newJSON:
		tempListe = []
		isBreak = False
		for j in oldJSON:

			if(i[1] == j[1] and i[2] == j[2] and i[3] == j[3] and i[6] == j[6] and i[7] == j[7]):
				i[0] = j[0]
				oldJSON.remove(j)
				isBreak = True
				break
			elif(i[1] == j[1]):
				tempListe.append(j)

		if tempListe:
			match = percentageMatch(tempListe, i, threshold, widthMeta, heightMeta)

			try:
				i[0] = match[0]
				oldJSON.remove(match)
			except:
				i[0] = counter
				counter += 1
		elif finalJSONID and isBreak == False:
			i[0] = finalJSONID.pop(0)



"""
	Generates a percentage match on elements, and set the old ID to the new element if it is the same
"""
def percentageMatch(tempListe, elementToCheck, THRESHOLD, widthMeta, heightMeta):
	#NUMBER = 250
	print(widthMeta)
	print(heightMeta)
	for currentElement in tempListe:
		percentage = abs((currentElement[2]-elementToCheck[2])/widthMeta) + abs((currentElement[3]-elementToCheck[3])/heightMeta) + abs((currentElement[6]-elementToCheck[6])/widthMeta) + abs((currentElement[7]-elementToCheck[7])/heightMeta)
		currentElement.append(percentage)

	tempListe.sort(key=lambda x: x[8])

	if(tempListe[0][10] < THRESHOLD):
		del tempListe[0][-1]
		return tempListe[0]
	else:
		return None

"""
	Parses JSON structure
"""
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

		meta = data["meta"]
		for e in data.items():
			if e[0] != "meta":
				readElementForID(e[1][1], test)
	return test, data, meta

"""
	Initializes the config file containing the user defined elements
"""
def configSetup():
	Config = configparser.RawConfigParser()
	Config.read("colorTypes.ini")
	readConfigFile(Config)

"""
	Reads the config file
"""
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


"""
	Converts hex to rgb
"""
def hex_to_rgb(value):
	value = value.lstrip('#')
	lv = len(value)
	return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

"""
	Saves the correct main elements to the main file
"""
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
		print(Fore.RED + color + " - is not a valid color and object will be ignored" + Style.RESET_ALL
			+"\n\tRead the documentation to add your own colors and corresponding elements.")
"""
	Saves the correct code to the header file
"""
def saveIOSobjectH(color, elementId, listenH, newListeH):
	if(color in listenH):
		name = listenH[color][0][0] + str(elementId)
		headerElement = listenH[color][1][0]
		newItem = str(headerElement).replace("NAME", str(name))
		newListeH.append(newItem)
"""
	Saves the correct adding code to the main file
"""
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
		relX = element["relX"]
		relY = element["relY"]
		width = element["width"]
		height = element["height"]
		parent = element["parent"]
		parentColor = element['parentColor']

		newListe.append([elementId, color, posX, posY, relX, relY, width, height, parent, parentColor])

		if len(contentStructure) > 0:
			for i in range (0, len(contentStructure)):
				readElementForNewListe(contentStructure[str(i)][1], newListe)


def readElementForID(element, test):
		elementId = element['id']
		test.append(elementId)
		contentStructure = element["content"]

		if len(contentStructure) > 0:
			for i in range (0, len(contentStructure)):
				readElementForID(contentStructure[str(i)][1], test)

def readElement(element, newListeM, newListeH, newListeMP):
	elementId = element['id']
	color = element["color"]
	posX = element["x"]
	posY = element["y"]
	relX = element["relX"]
	relY = element["relY"]
	width = element["width"]
	height = element["height"]
	parent = element["parent"]
	parentColor = element['parentColor']
	contentStructure = element["content"]

	saveIOSobjectM(color, elementId, relX, relY, width, height, listenM, newListeM)
	saveIOSobjectH(color, elementId,listenH, newListeH)
	saveIOSobjectMP(newListeMP, parentColor, elementId, parent, listenMP, color)

	if len(contentStructure) > 0:
		for i in range (0, len(contentStructure)):
			try:
				readElement(contentStructure[str(i)][1], newListeM, newListeH, newListeMP)
			except:
				readElement(contentStructure[i][1], newListeM, newListeH, newListeMP)

def prepareFiles(outputPath, filename, fileType, appName):
	outputPath = outputPath + "/" + appName
	file1 = open(outputPath + "/" + filename + "." + fileType , "r")
	fileTemp1 = open(outputPath + "/temp.txt", "w")
	for line in file1:
		if re.search('\{\{viewname\}\}', line):
			fileTemp1.write(re.sub('\{\{viewname\}\}', filename, line))
		else :
			fileTemp1.write(line)
	file1.close()
	fileTemp1.close()

	file2 = open(outputPath + "/" + filename + "." + fileType , "w")
	fileTemp2 = open(outputPath + "/temp.txt", "r")

	for line in fileTemp2:
		file2.write(line)

	file2.close()
	fileTemp2.close()
	os.remove(outputPath + "/temp.txt")



def replaceText(templatePath, fileType, filename, elements, elements2, appName):
	templatePath = templatePath+"/" + appName
	file1 = open(templatePath + "/" + filename + "Base." + fileType , "r")
	file2 = open(templatePath + "/NewFile.txt", "w")


	for line in file1:
		insertNameHere = re.search('\{\{viewname\}\}', line)
		content = re.match('\{\{content\}\}', line)
		if(content):
			file2.write("/* Declearing elements */\n")
			for i in elements:
				file2.write(i + "\n")
			if(elements2 != None):
				file2.write("\n")
				file2.write("/* Adding elements */\n")
				for j in elements2:
					file2.write(j + "\n")
		elif (insertNameHere):
			file2.write(re.sub('\{\{viewname\}\}', filename+"Base", line))
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

	os.remove(templatePath + '/NewFile.txt')

"""
	If the project is used as a module, it set the input parameters to the CLI tool.
	It then run the main iOS function.
"""
if __name__== "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("jsonPath", help="Path to JSON structure") #NB! Vi kan også bruke styles her! :)
	ap.add_argument("outputPath", help="Output directory")
	ap.add_argument("-t","--threshold", help="Defined threshold for view update",nargs='?',type=int, default=15)
	ap.add_argument("-v", "--verbose", help="Verbose output", action="store_true", default=False)
	ap.add_argument("-f", "--force", help="Force continue. May result in overwrite and unexpected results.", action="store_true", default=False)
	args = ap.parse_args()

	appName = os.path.basename(os.path.normpath(args.outputPath))
	print("OUTPUT: " + args.outputPath)
	print("APP NAME: " + appName)

	initProject(args.outputPath, args.verbose, args, appName)
