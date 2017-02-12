import argparse
import json
import os.path
#from htmlGen import htmlUtils
#import htmlUtils
from colorama import Fore, Back, Style
from collections import OrderedDict
from pprint import pprint



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

		template = template.replace('$cssLink',  "styles.css")

		pprint(template)

		if externalRun : from htmlGen import htmlUtils 
		else : import htmlUtils

		html = ""
		css = ""
		counter = 0
		for e in data.items(): # iterate root elements
			someHTML, someCSS = readElement(e[1][1])
			html += someHTML
			css += someCSS
			
		print("DONE PARSING JSON")
		print("Got this structure: ")
		#pprint(html)

		pprint("")
		pprint("And this css:")
		#pprint(css)

		template = template.replace("$content", html)

		print("The new html:")
		pprint(template)

		fileHTML.write(template)
		fileCSS.write(css)

		
		fileHTML.close()
		fileCSS.close()
		print(Fore.GREEN + "HTML generator done" + Fore.RESET)


cssClasses = {}
"""
	element is an ordered dict
"""
def readElement(element):
	counter += 1
	elementId = element['id']
	color = element["color"]
	posX = element["x"]
	posY = element["y"]
	width = element["width"]
	height = element["height"]
	contentStructure = element["content"]
	print()

	innerHTML = "Lorem"
	innerCSS = ""
	if len(contentStructure) > 0:
		innerHTML, innerCSS = readElement(contentStructure['0'][1])
	
	tekst = "<{0} class='{0}-{1}' width='{2}' height='{3}'>{4}</{0}>\n".format("div", counter, width, height, innerHTML)
	# check if css class entry already exists and if not, add it to the list.
	css = ".{0}-{1} {2}\n \tbackground-color: {6}; \n\tmargin-left:{3}px; \n\tmargin-top:{4}px; \n{5}\n".format("div", counter, "{", posX, posY, "}", color) + innerCSS
	try:
		cssClasses["div",color].append([color, posX, posY])
	except KeyError:
		cssClasses["div",color] = [color, posX, posY]

	return tekst, css

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

