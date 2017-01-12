#!/usr/local/bin/env python3

import argparse
import json
import os.path
from PIL import Image
import utils


parser = argparse.ArgumentParser()

parser = utils.argparserSetup(parser)

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


utils.checkIfDirExists(args)


print("DONE!")



# TODO: Call the image parser here....



# TODO: Call the transpiler here...
