import argparse
import json
import os.path
from colorama import Fore, Back, Style
from collections import OrderedDict
from pprint import pprint

cssClasses = []

def parseJson(jsonPath, title, outputPath, debug, externalRun=False):
	if debug: print("Running json parser...")

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

		#pprint(template)

		if externalRun : from htmlGen import htmlUtils
		else : import htmlUtils

		html = ""
		for e in data.items(): # iterate root elements
			html += readElement(e[1][1])
			
		print("Done parsing JSON and generating html")

		template = template.replace('$cssLink',  "styles.css")
		template = template.replace("$title", title)
		template = template.replace("$content", html)

		css = generateCSS()

		print("Done generating css")

		fileHTML.write(template)
		fileCSS.write(css)

		print("Done writing to file")
		
		fileHTML.close()
		fileCSS.close()
		print(Fore.GREEN + "HTML generator done" + Fore.RESET)


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

	innerHTML = "Lorem" # must be here or else the html wont show anythong...
	if len(contentStructure) > 0:
		for i in range(0, len(contentStructure)):
			innerHTML += readElement(contentStructure[str(i)][1]) # REDO real loop
			
	
	# NEED TO GO FROM COLOR TO TAG HERE!

	tekst = "<{0} class='{0}-{5}-{6}' width='{2}' height='{3}'>{4}</{0}>\n".format("div", color, width, height, innerHTML, posX, posY)
	# check if css class entry already exists and if not, add it to the list.
	
	if not ("div", color, posX, posY) in cssClasses:
		cssClasses.append(("div", color, posX, posY))
    
	return tekst

if __name__== "__main__":

	# import htmlUtils

	#Initialize argument parser
	ap = argparse.ArgumentParser()
	ap.add_argument("JSONpath", help="Path to JSON structure")
	ap.add_argument("title", help="The title of the web page")
	ap.add_argument("outputPath", help="Output directory")
	ap.add_argument("-v", "--verbose", help="Verbose output", action="store_true", default=False)
	args = ap.parse_args()

	#Start the parser
	parseJson(args.JSONpath, args.title, args.outputPath, args.verbose)
