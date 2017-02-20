import argparse
import json
import os.path
from colorama import Fore, Back, Style
from collections import OrderedDict
from pprint import pprint
import configparser

cssClasses = []
colorTypes = {}

def parseJson(jsonPath, title, outputPath, debug):
	if debug: print("Running json parser...")

	Config = configparser.RawConfigParser()
	Config.read("colorTypes.ini")
	readConfigFile(Config)

	if debug: print("Config files read")

	#Open JSON file and load content
	with open(jsonPath) as data_file:
		data = OrderedDict()
		try:
			data = json.load(data_file, object_pairs_hook=OrderedDict)
		except ValueError:
			print(Fore.RED + "Something went wrong. Could not read JSON. Is the JSON structure correct?" + Style.RESET_ALL)
			return
		#Check if output folder exists, and if not, create a dir
		if not os.path.exists(outputPath):
			os.makedirs(outputPath)

		#Open/create the index html file
		fileHTML = open(outputPath + "/index.html", "w")
		fileCSS = open(outputPath + "/styles.css", "w")
		fileTemplate = open("html_template.txt", "r")

		template = fileTemplate.read()

		html = ""
		for e in data.items(): # iterate root elements
			if e[0] != "meta":
				html += readElement(e[1][1])
			
		if debug: print("Done parsing JSON and generating html")

		template = template.replace('$cssLink',  "styles.css")
		template = template.replace("$title", title)
		template = template.replace("$content", html)

		css = generateCSS()

		if debug: print("Done generating css")

		fileHTML.write(template)
		fileCSS.write(css)

		if debug: print("Done writing to file")
		
		fileHTML.close()
		fileCSS.close()
		print(Fore.GREEN + "HTML generator done" + Fore.RESET)


def readConfigFile(config):
	options = config.options("color")
	for option in options:
		colorTypes["#" + option] = config.get("color", option)


def generateCSS():
	css = ""
	for e in cssClasses:
		css = css + ".{0}-{1}-{2} {{\n \tbackground-color: {3}; \n\tmargin-left:{1}px; \n\tmargin-top:{2}px; \n}}\n".format(e[0], e[2], e[3], e[1])
	return css

"""
	element is an ordered dict
"""
def readElement(element):
	elementId = element['id']
	color = element["color"]
	posX = element["x"]
	posY = element["y"]
	width = element["width"]
	height = element["height"]
	contentStructure = element["content"]
	tag = colorTypes[color]

	innerHTML = "Lorem" # must be here or else the html wont show anythong...
	if len(contentStructure) > 0:
		for i in range(0, len(contentStructure)):
			innerHTML += readElement(contentStructure[str(i)][1])
				
	tekst = "<{0} class='{0}-{5}-{6}' width='{2}' height='{3}'>{4}</{0}>\n".format(tag, color, width, height, innerHTML, posX, posY)
	
	# check if css class entry already exists and if not, add it to the list.
	if not (tag, color, posX, posY) in cssClasses:
		cssClasses.append((tag, color, posX, posY))
	
	return tekst

if __name__== "__main__":

	#Initialize argument parser
	ap = argparse.ArgumentParser()
	ap.add_argument("JSONpath", help="Path to JSON structure")
	ap.add_argument("title", help="The title of the web page")
	ap.add_argument("outputPath", help="Output directory")
	ap.add_argument("-v", "--verbose", help="Verbose output", action="store_true", default=False)
	args = ap.parse_args()

	#Start the parser
	parseJson(args.JSONpath, args.title, args.outputPath, args.verbose)
