#!/usr/local/bin/env python3

import argparse
import json
import os.path
from PIL import Image

from wrapper import wrapperUtils 
from htmlGen import htmlGen
from imageParser import imageParser
from colorama import Fore, Back, Style


#Prepare argument parser
parser = argparse.ArgumentParser()
parser = wrapperUtils.argparserSetup(parser)
args = parser.parse_args()

#If debug, print input arguments
if args.verbose:
	print(Style.DIM + "This is the path for the image: " + Style.RESET_ALL + Fore.GREEN + args.inputImage + Fore.RESET)
	print(Style.DIM + "This is the path for the output project: "+ Style.RESET_ALL + Fore.BLUE + args.outputPath + Fore.RESET)
	print(Style.DIM + "This is the name of the project: "+ Style.RESET_ALL + Fore.YELLOW + args.projectName + Fore.RESET)

	if(args.ios): print("iOs is chosen")
	elif (args.html): print("HTML is chosen")
	elif (args.android): print("Android is chosen")

#Check and prepare the file structure needed
wrapperUtils.checkIfDirExists(args)

#Generate a full path to the selected image
fullPath = os.path.abspath(args.inputImage)
if args.verbose: print(Fore.YELLOW + "Full file path to image: "+ Style.RESET_ALL + fullPath)

#Read the image and create a JSON structure
pathToJson = imageParser.parseImage(fullPath, args.outputPath)

#Generate html according to the JSON 
htmlGen.parseJson(pathToJson + "/testFil.json", args.projectName, args.outputPath +  "/" + args.projectName, args.verbose)

print(Fore.GREEN + "Done" + Style.RESET_ALL)
