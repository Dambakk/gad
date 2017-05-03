import argparse
import json
import os.path
from colorama import Fore, Back, Style
from collections import OrderedDict
from pprint import pprint
import configparser
from bs4 import BeautifulSoup as bs

cssClasses = []
colorTypes = {}

htmlElements = {}

"""
	Main function.
"""
def parseJson(jsonPath, title, outputPath, debug):

	#Read config file
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

		#Parse the JSON and convert it to HTML
		html = ""
		for e in data.items(): # iterate root elements
			if e[0] != "meta":
				html += readElement(e[1][1])
			
		#Make the generated html look good w/indention and stuff
		soup1 = bs(html, "html.parser")
		prettyHTML1 = soup1.prettify()

		#Insert all user specific variables to template html
		template = template.replace('$cssLink',  "styles.css")
		template = template.replace("$title", title)
		template = template.replace("$content", prettyHTML1)

		#Make the complete HTML look good.
		soup2 = bs(template, "html.parser")
		prettyHTML2 = soup2.prettify()

		if debug: print("Done parsing JSON and generating html")

		#Generate css based on HTML
		css = generateCSS()

		if debug: print("Done generating css")

		#Write css and HTML to file
		fileHTML.write(prettyHTML2)
		fileCSS.write(css)
		fileHTML.close()
		fileCSS.close()

		if debug: print("Done writing to file")
		
		#Done! Inform user
		print(Fore.GREEN + "HTML generator done" + Fore.RESET)
		print("The result can be found at this location: ")
		print(Fore.YELLOW + os.path.abspath(outputPath) + Fore.RESET)


"""
	Read the config file for the user-specific colors and their
	corresponding HTML elements.
"""
def readConfigFile(config):
	
	#Read the "color <-> tag"-relationship
	for option in config.options("tags"):
		colorTypes["#" + option] = config.get("tags", option)

	#Read the "color <-> HTML"-relationship
	for option in config.options("html-elements"):
		htmlElements["#" + option] = config.get("html-elements", option)


"""
	Iterates the information about the HTML elements and generates
	corresponding CSS and returns it.

	Returns the generated CSS.
"""
def generateCSS():
	css = ""
	for e in cssClasses:
		css = css + ".{0}-{1}-{2}-{4}-{5} {{\n \tbackground-color: {3}; \n\tmargin-left:{1}px; \n\tmargin-top:{2}px; \n\twidth:{4}px; \n\theight:{5}px; \n}}\n".format(e[0], e[2], e[3], e[1], e[4], e[5])
	return css


"""
	Reads a JSON-/ordered dict-element and iterates the childs of
	an element, if any, in a recirsive way. Then it creates a HTML
	element of the parsed JSON element according to the stored color
	and inserts the data from the JSON into the html. 

	Returns the generated HTML.
"""
def readElement(element):
	#Read the info from the JSON
	elementId = element['id']
	color = element["color"]
	posX = element["x"]
	posY = element["y"]
	relX = element["relX"]
	relY = element["relY"]
	width = element["width"]
	height = element["height"]
	contentStructure = element["content"]
	tag = colorTypes[color]

	#Iterate the children/content if any
	innerHTML = "Lorem ipsum" # must be something or else the html wont show anything when openend in a browser...
	if len(contentStructure) > 0:
		for i in range(0, len(contentStructure)):
			innerHTML += readElement(contentStructure[str(i)][1])
				
	#Insert the data from JSON into HTML	
	html = htmlElements[color] 
	if "CSSCLASS" in html:
		html = str(html).replace("CSSCLASS", str(tag+"-"+str(relX)+"-"+str(relY)+"-"+str(width)+"-"+str(height)))
	if "CONTENT" in html:
		html = str(html).replace("CONTENT", str(innerHTML))

	# check if css class entry already exists and if not, add it to the list.
	if not (tag, color, relX, relY, width, height) in cssClasses:
		cssClasses.append((tag, color, relX, relY, width, height))
	
	return html


# Main entry point
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
