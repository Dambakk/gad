
import os.path
import argparse

#TODO: Need a better way to generate file endings. Maybe only generate file endings when creating necessary files
def checkWhatFileType(args):
	if(args.ios):
		return ".ipa";
	elif(args.html):
		return ".html"
	elif(args.android):
		return ".txt"


#TODO: Needs work...
def checkIfDirExists(args):
	newFolder = args.outputPath + "/" + args.projectName
	fileName = checkWhatFileType(args)
	if not os.path.exists(args.outputPath) or not os.path.exists(newFolder):
		print("Creating a folder " + newFolder + " in " + args.outputPath)
		os.makedirs(newFolder)
		f = open(newFolder+"/testFil" + fileName, "w+").close
		print(newFolder)
	else:
		#Ask user if he wants to overwrite what is already there?
		answer = input("Are you sure you want to overwrite? (y/n) ")
		print("Your answer: " + answer)
		print("this path is already taken, try another")
	return;


def argparserSetup(parser):
	parser.add_argument("inputImage", help="Path to the image to generate GUI from")
	parser.add_argument("outputPath", help="Path to where the generated project will be")
	parser.add_argument("projectName", help="Name of the project")

	platform = parser.add_mutually_exclusive_group(required=True)
	platform.add_argument("--ios", help="Create a iOs project", action="store_true")
	platform.add_argument("--html", help="Create a html web page", action="store_true")
	platform.add_argument("--android", help="Create an android project", action="store_true")

	parser.add_argument("-v", "--verbose", help="Verbose output level", action="store_true", default=False)

	return parser
