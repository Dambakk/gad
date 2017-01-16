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



"""
print("JSON Path:  " + args.JSONpath)

if os.path.isfile(args.JSONpath):
	file = open("index.html", "w+")

	with open(args.JSONpath) as json_data:
		data = json.load(json_data)
		htmlUtils.prepareHTML(file, args.title)

		for element in data:
			type = element["type"]
			content = element["content"]
			color = element["color"]
			print(type + " - " + content)
			htmlUtils.insertElement(type, content, color, file)

		htmlUtils.endHTML(file)


	file.close();
	print("Done")

	"""
