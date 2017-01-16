import argparse
import json
from htmlGen import htmlUtils
import os.path


"""
ap = argparse.ArgumentParser()
ap.add_argument("JSONpath", help="Path to JSON structure")
ap.add_argument("title", help="The title of the web page")

args = ap.parse_args()
"""



def parseJson(jsonPath, title, outputPath):
	print("JSON Path:  " + jsonPath)

	if os.path.isfile(jsonPath):
		file = open(outputPath + "/index.html", "w+")

		with open(jsonPath) as json_data:
			data = json.load(json_data)
			htmlUtils.prepareHTML(file, title)

			for element in data:
				type = element["type"]
				content = element["content"]
				color = element["color"]
				print(type + " - " + content)
				htmlUtils.insertElement(type, content, color, file)

			htmlUtils.endHTML(file)


		file.close();
		print("HTML generator done")

	
