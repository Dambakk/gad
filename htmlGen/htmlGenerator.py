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
		file = open(outputPath + "/index.html", "w")

		if externalRun : from htmlGen import htmlUtils 
		else : import htmlUtils

		html = ""
		for e in data.items():
			html += readElement(e[1][1], file)
			
		print("DONE PARSING JSON")
		print("Got this structure: ")
		pprint(html)
		file.write(html)

		"""


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

		"""
		file.close();
		print(Fore.GREEN + "HTML generator done" + Fore.RESET)

"""
	element is an ordered dict
"""
def readElement(element, file):
	elementId = element['id']
	color = element["color"]
	posX = element["x"]
	posY = element["y"]
	width = element["width"]
	height = element["height"]
	contentStructure = element["content"]
	print()
	print("Element: ", elementId, color )

	#htmlUtils.insertElement("div", "lorem", color, posX, posY, width, height, file)
	content = "Lorem"
	if len(contentStructure) > 0:
		print("Found some content")
		print(contentStructure['0'][1])
		#Should might be another loop here to loop through the content instead of hard coding in '0'
		content = readElement(contentStructure['0'][1], file)
	
	tekst = "<{0} style='background-color:{1}; margin-left:{2}px; margin-top:{3};' width='{4}' height='{5}'>{6}</{0}>\n".format("div", color, posX, posY, width, height, content)

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

