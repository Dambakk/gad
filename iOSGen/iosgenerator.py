#!/usr/local/bin/env python3
import os
import argparse
from colorama import Fore, Back, Style
from distutils.dir_util import copy_tree
import re
import fileinput
from colorama import Fore, Back, Style
from collections import OrderedDict
import json

"""
@property(nonatomic, strong) UIView *view1;
@property(nonatomic, strong) UIView *view2;
@property(nonatomic, strong) UILabel *label1;
@property(nonatomic, strong) UIImageView *imageView1;
@property (nonatomic, strong) UIButton *button1;
@property (nonatomic, assign) int myInt;


self.view.backgroundColor = [UIColor colorWithRed:1 green:1 blue:1 alpha:1];

//self.view.backgroundColor = [UIColor colorWithRed:0xea/255.0 green:0xea/255.0 blue:0xea/255.0 alpha:1];


self.view2 = [[UIView alloc] initWithFrame:CGRectMake(50, 50, 100, 100)];
self.view2.backgroundColor = [UIColor redColor];
[self.view addSubview:self.view2];

self.label1 = [[UILabel alloc] initWithFrame:CGRectMake(10, 10, 200, 20)];
self.label1.text = @"Hello world!";
[self.label1 sizeToFit];
[self.view addSubview:self.label1];

self.button1 = [[UIButton alloc] initWithFrame:CGRectMake(100, 200, 40, 40)];
self.button1.backgroundColor = [UIColor yellowColor];
[self.view addSubview:self.button1];

"""

listenM = {'#d41d01' : [["view"],["self.NAME = [[UIView alloc] initWithFrame:CGRectMake(posX, posY, width, height)];"], ["self.NAME.backgroundColor = [UIColor COLOR];"], ["[self.view addSubview:self.NAME];"]]}
listenH = {'#d41d01' : [["view"], ["@property(nonatomic, strong) UIView *NAME;"]]}

def copyProject(outputPath, args):
    if(args.ios):
        fromDirectory = "DemoApp"
        toDirectory = outputPath
        copy_tree(fromDirectory, toDirectory)

        newListeM = []
        newListeH = []
        #TODO : Generate extractor code from JSON

        with open(args.jsonPath) as data_file:
            data = OrderedDict()
            try:
                data = json.load(data_file, object_pairs_hook=OrderedDict)
            except ValueError:
        	    print(Fore.RED + "Something went wrong. Could not read JSON. Is the JSON structure correct?" + Style.RESET_ALL)
        	    return

            for e in data.items():
                readElement(e[1][1], newListeM, newListeH)

        print(newListeM, " is newListeM")
        print(newListeH, " is newListeH")
        print("        ")

        replaceText(outputPath, "m", newListeM)
        replaceText(outputPath, "h", newListeH)

        print("Done Dambikk")


def saveIOSobjectM(color, elementId, posX, posY, width, height, liste, newListeM):
    print(color, elementId, posX, posY, width, height, "  hahahadsfasdfasdfs")

    if(color in liste):
        name = liste[color][0][0] + str(elementId)
        newItem = ""
        for i in range(1, len(liste[color])):
            item = liste[color][i]

            if ("NAME" in item[0]):
                a = item[0]
                b = str(a).replace("NAME", str(name))
                newItem = b
            if ("posX" in item[0]):
                a = newItem
                b = str(a).replace("posX", str(posX))
                newItem = b
            if ("posY" in item[0]):
                a = newItem
                b = str(a).replace("posY", str(posY))
                newItem = b
            if ("width" in item[0]):
                a = newItem
                b = str(a).replace("width", str(width))
                newItem = b
            if ("height" in item[0]):
                a = newItem
                b = str(a).replace("height", str(height))
                newItem = b
            if ("COLOR" in item[0]):
                a = newItem
                b = str(a).replace("COLOR", "redColor")
                newItem = b
            newListeM.append(newItem)

    else:
        print("Not a valid color")

def saveIOSobjectH(color, elementId, listenH, newListeH):
    if(color in listenH):

        name = listenH[color][0][0] + str(elementId)
        a = listenH[color][1][0]

        b = str(a).replace("NAME", str(name))
        newListeH.append(b)


def readElement(element, newListeM, newListeH):
    elementId = element['id']
    color = element["color"]
    posX = element["x"]
    posY = element["y"]
    width = element["width"]
    height = element["height"]
    parent = element["parent"]
    contentStructure = element["content"]
    print(" ------- ")
    print("Element: ", elementId, color, posX, posY, width, height, parent)

    saveIOSobjectM(color, elementId, posX, posY, width, height, listenM, newListeM)
    saveIOSobjectH(color, elementId,listenH, newListeH)

    content = "Lorem"
    if len(contentStructure) > 0:
        #print("Found some content")
        #print(contentStructure['0'][1])
    		#Should might be another loop here to loop through the content instead of hard coding in '0'
        content = readElement(contentStructure['0'][1], newListeM, newListeH)


def replaceText(templatePath, fileType, elements):
    templatePath = templatePath+"/DemoApp"
    print(templatePath)
    file1 = open(templatePath + "/ViewControllerBase." + fileType , "r")
    file2 = open(templatePath + "/NewFile.txt", "w")

    for line in file1:
        matchObj = re.match('\{\{\[\]\}\}', line)
        if(matchObj):
            for i in elements:
                file2.write(i + "\n")
        else:
            #print(line)
            file2.write(line)
    file1.close()
    file2.close()

    file3 = open(templatePath + "/ViewControllerBase." + fileType , "w")
    file4 = open(templatePath + "/NewFile.txt", "r")

    for line in file4:
        file3.write(line)

    file3.close()
    file4.close()

    if(os.path.exists(templatePath + '/NewFile.txt')):
        os.remove(templatePath + '/NewFile.txt')

if __name__== "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonPath", help="Path to JSON structure")
    #ap.add_argument("title", help="The title of the web page")
    ap.add_argument("outputPath", help="Output directory")
    #ap.add_argument("jsonPath", help="Path to JSON structure")
    #ap.add_argument("test", help="hihi")
    platform = ap.add_mutually_exclusive_group(required=True)
    platform.add_argument("--ios", help="Create a iOs project", action="store_true")
    platform.add_argument("--html", help="Create a html web page", action="store_true")
    platform.add_argument("--android", help="Create an android project", action="store_true")
    ap.add_argument("-v", "--verbose", help="Verbose output", action="store_true", default=False)
    args = ap.parse_args()
    #Start the parser
    copyProject(args.outputPath, args)
