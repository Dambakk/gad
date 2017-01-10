#!/usr/bin/env python3

import argparse
import json
import os.path
from PIL import Image


parser = argparse.ArgumentParser()

parser.add_argument("inputImage", help="Path to the image to generate GUI from")
parser.add_argument("outputPath", help="Path to where the generated project will be")
parser.add_argument("projectName", help="Name of the project")

platform = parser.add_mutually_exclusive_group(required=True)
platform.add_argument("--ios", help="Create a iOs project", action="store_true")
platform.add_argument("--html", help="Create a html web page", action="store_true")
platform.add_argument("--android", help="Create an android project", action="store_true")

logging = parser.add_mutually_exclusive_group(required=False)
logging.add_argument("-s", "--silent", help="Silent output level", action="store_true", default=False)
logging.add_argument("-d", "--default", help="Default ouput level", action="store_true", default=False)
logging.add_argument("-v", "--verbose", help="Verbose output level", action="store_true", default=False)

parser.add_argument("--debug", help="Run in debug mode", default=False)

args = parser.parse_args()

print("This is the path for the image: "+ args.inputImage)
print("This is the path for the output project: "+ args.outputPath)
print("This is the name of the project: "+ args.projectName)


if(args.ios): print("iOs is chosen")
elif (args.html): print("HTML is chosen")
elif (args.android): print("Android is chosen")


outputLevel = 2
if(args.silent): outputLevel = 1
if(args.verbose): outputLevel = 3

if(outputLevel == 1): print("Silent mode")
elif(outputLevel == 2): print("Default output mode")
elif(outputLevel == 3): print("Verbose output level")

print("")
print("Reading file...")
print("")

x = [1, "simple", "list"] #A JSON example

if not(args.inputImage.lower().endswith(".png")):
	print("File should be an image file (png)")
	#Todo: Return error here

if not(os.path.exists(args.inputImage)):
	print("File does not exist")
	#Todo: Return error here

# TODO: Do other pre checkings here...


#Check if there is the file is

def checkWhatFileType():
	if(args.ios):
		return ".ipa";
	elif(args.html):
		return ".html"
	elif(args.android):
		return ".txt"

def checkIfDirExists():
	newFolder = args.outputPath + "/" + args.projectName
	fileName = checkWhatFileType()
	if not os.path.exists(args.outputPath):
		print("there is no such directory!!")
		os.makedirs(newFolder)
		f = open(newFolder+"/testFil" + fileName, "w+").close
		print(newFolder)
	else:
		print("this path is already taken, try another")
	return;

checkIfDirExists()



"""
print("File exists")
im = Image.open(args.inputImage)
im.rotate(45).show();
"""

"""
with open(args.inputImage, "r+") as f: # with keyword instead of try catch
	for line in f:
		print(line)
	json.dump(x, f)
"""


# TODO: Call the image parser here....



# TODO: Call the transpiler here...
