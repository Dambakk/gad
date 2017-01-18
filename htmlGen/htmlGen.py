import argparse
import json
import htmlUtils
import os.path
from colorama import Fore, Back, Style


def parseJson(jsonPath, title, outputPath, debug):
	if debug: print("Running json parser...")
	
	#Open JSON file and load content
	with open(jsonPath) as data_file:

		try:
			data = json.load(data_file)
		except ValueError:
			print(Fore.RED + "Something went wrong. Could not read JSON. Is the JSON structure correct?" + Style.RESET_ALL)
			return
		#Check if output folder exists, and if not, create a dir
		if not os.path.exists(outputPath):
			os.makedirs(outputPath)

		#Open/create the index html file
		file = open(outputPath + "/index.html", "w")

		#Prepare html file (add head, title, body, etc)
		htmlUtils.prepareHTML(file, title)

		#Loop through elements in JSON and create corresponding html elements
		for element in data:
			#If key is not found there will be an exception...
			type = element["type"]
			content = element["content"]
			color = element["color"]
			posX = element["x"]
			posY = element["y"]
			width = element["width"]
			height = element["height"]
			if debug: print(Fore.YELLOW + "Creating an element: " + Fore.WHITE + type + Fore.YELLOW + " - " + Fore.WHITE + content + Style.RESET_ALL)
			htmlUtils.insertElement(type, content, color, posX, posY, width, height, file)

		#Add ending tags to html file
		htmlUtils.endHTML(file)

		file.close();
		print(Fore.GREEN + "HTML generator done" + Fore.RESET)


#Initialize argument parser
ap = argparse.ArgumentParser()
ap.add_argument("JSONpath", help="Path to JSON structure")
ap.add_argument("title", help="The title of the web page")
ap.add_argument("outputPath", help="Output directory")
ap.add_argument("-v", "--verbose", help="Verbose output", action="store_true", default=False)
args = ap.parse_args()

#Start the parser
parseJson(args.JSONpath, args.title, args.outputPath, args.verbose)

