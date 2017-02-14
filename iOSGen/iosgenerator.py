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
import configparser

"""
listenM = {
'#d41d01' : [["view"],["self.NAME = [[UIView alloc] initWithFrame:CGRectMake(posX, posY, width, height)];"], ["self.NAME.backgroundColor = [UIColor COLOR];"]],
'#9aaa01' : [["button"], ["self.NAME = [[UIButton alloc] initWithFrame:CGRectMake(posX, posY, width, height)];"], ["self.NAME.backgroundColor = [UIColor COLOR];"]],
'#0228d4' : [["dambakk"], ["self.NAME = [[UIDambakk alloc] initWithFrame:CGRectMake(posX, posY, width, height)];"], ["self.NAME.backgroundColor = [UIColor COLOR];"]]
}

{
'#0228d4': [['dambakk'], ['self.NAME = [[UIDambakk alloc] initWithFrame:CGRectMake(posX, posY, width, height)];'], ['self.NAME.backgroundColor = [UIColor COLOR];']], 
'#9aaa01': [['button'], ['self.NAME = [[UIButton alloc] initWithFrame:CGRectMake(posX, posY, width, height)];'], ['self.NAME.backgroundColor = [UIColor COLOR];']], 
'#d41d01': [['view'], ['self.NAME = [[UIView alloc] initWithFrame:CGRectMake(posX, posY, width, height)];'], ['self.NAME.backgroundColor = [UIColor COLOR];']]
} 

listenMP = {
"default" : ["[self.view addSubview:self.NAME];"],  
'#d41d01' : ["[self.viewID addSubview:self.NAME];"], 
'#9aaa01' : ["[self.buttonID addSubview:self.NAME];"],
'#0228d4' : ["[self.dambakkID addSubview:self.NAME;"]
}

listenH = {
'#d41d01' : [["view"], ["@property (nonatomic, strong) UIView *NAME;"]], 
'#9aaa01' : [["button"], ["@property (nonatomic, strong) UIButton *NAME;"]],
'#0228d4' : [["Dambakk"], ["@property (nonatomic, superstrong) UIDambakk *NAME;"]]
}
"""

listenM = {}
listenMP = {}
listenH = {}

def copyProject(outputPath, args):
    if(args.ios):
        fromDirectory = "DemoApp"
        toDirectory = outputPath
        print("Output path: ", outputPath)
        copy_tree(fromDirectory, toDirectory)

        configSetup()

        newListeM = []
        newListeH = []
        newListeMP = []

        with open(args.jsonPath) as data_file:
            data = OrderedDict()
            try:
                data = json.load(data_file, object_pairs_hook=OrderedDict)
            except ValueError:
        	    print(Fore.RED + "Something went wrong. Could not read JSON. Is the JSON structure correct?" + Style.RESET_ALL)
        	    return

            for e in data.items():
                readElement(e[1][1], newListeM, newListeH, newListeMP)
        print()
        print("Done reading elements")

        replaceText(outputPath, "m", newListeM, newListeMP)
        replaceText(outputPath, "h", newListeH, None)

        print("Done Dambikk") # haha

def configSetup():
    Config = configparser.RawConfigParser()
    Config.read("colorTypes.ini")
    readConfigFile(Config)

def readConfigFile(config):
    options1 = config.options("listenM")
    for option in options1:
        listenM["#" + option] = eval(config.get("listenM", option))

    options2 = config.options("listenMP")
    for option in options2:
        if str(option) == 'default':
            listenMP[option] = eval(config.get("listenMP", option))
        else:
            listenMP["#" + option] = eval(config.get("listenMP", option))
    options3 = config.options("listenH")
    for option in options3:
        listenH["#" + option] = eval(config.get("listenH", option))

def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def saveIOSobjectM(color, elementId, posX, posY, width, height, liste, newListeM):
    if(color in liste):
        name = liste[color][0][0] + str(elementId)
        newItem = ""
        for i in range(1, len(liste[color])):
            item = liste[color][i]
            if ("NAME" in item[0]):
                newItem = str(item[0]).replace("NAME", str(name))
            if ("posX" in item[0]):
                newItem = str(newItem).replace("posX", str(posX))
            if ("posY" in item[0]):
                newItem = str(newItem).replace("posY", str(posY))
            if ("width" in item[0]):
                newItem = str(newItem).replace("width", str(width))
            if ("height" in item[0]):
                newItem = str(newItem).replace("height", str(height))
            if ("COLOR" in item[0]):
                (r,g,b) = hex_to_rgb(color)
                rgbColor = "colorWithRed:{0}/255.0 green:{1}/255.0 blue:{2}/255.0 alpha:1".format(r,g,b)
                newItem = str(newItem).replace("COLOR", rgbColor) 
            newListeM.append(newItem)
    else:
        print("Not a valid color")

def saveIOSobjectH(color, elementId, listenH, newListeH):
    if(color in listenH):
        newitem = ""
        name = listenH[color][0][0] + str(elementId)
        a = listenH[color][1][0]
        newItem = str(a).replace("NAME", str(name))
        newListeH.append(newItem)

def saveIOSobjectMP(newListeMP, parentColor, elementId, parent, listenMP, color):
    if(parent != -1):
        if(color in listenMP):
            name = listenM[color][0][0] + str(elementId)
            item = listenMP[parentColor][0]
            newItem = ""
            if("ID" in item[0]):
                newItem = str(item[0]).replace("ID", str(parent))
            if("NAME" in item[0]):
                newItem = str(newItem).replace("NAME", str(name))
            newListeMP.append(newItem)
    else:
        if(color in listenMP):
            item = listenMP['default'][0]
            name = listenM[color][0][0] + str(elementId)
            newItem = ""
            if("NAME" in item[0]):
                newItem = str(item[0]).replace("NAME", str(name))
            newListeMP.append(newItem)




def readElement(element, newListeM, newListeH, newListeMP):
    elementId = element['id']
    color = element["color"]
    posX = element["x"]
    posY = element["y"]
    width = element["width"]
    height = element["height"]
    parent = element["parent"]
    parentColor = element['parentColor']
    contentStructure = element["content"]

    saveIOSobjectM(color, elementId, posX, posY, width, height, listenM, newListeM)
    saveIOSobjectH(color, elementId,listenH, newListeH)
    saveIOSobjectMP(newListeMP, parentColor, elementId, parent, listenMP, color)

    content = "Lorem"
    if len(contentStructure) > 0:
        for i in range (0, len(contentStructure)):
            content = readElement(contentStructure[str(i)][1], newListeM, newListeH, newListeMP)
      

def replaceText(templatePath, fileType, elements, elements2):
    templatePath = templatePath+"/DemoApp"
    file1 = open(templatePath + "/ViewControllerBase." + fileType , "r")
    file2 = open(templatePath + "/NewFile.txt", "w")

    for line in file1:
        matchObj = re.match('\{\{\[\]\}\}', line)
        if(matchObj):
            file2.write("/* Declearing elements */\n")
            for i in elements:
                file2.write(i + "\n")
            if(elements2 != None):
                file2.write("\n")
                file2.write("/* Adding elements */\n")
                for j in elements2:
                    file2.write(j + "\n")
        else:
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
    ap.add_argument("outputPath", help="Output directory")
    platform = ap.add_mutually_exclusive_group(required=True)
    platform.add_argument("--ios", help="Create a iOs project", action="store_true")
    platform.add_argument("--html", help="Create a html web page", action="store_true")
    platform.add_argument("--android", help="Create an android project", action="store_true")
    ap.add_argument("-v", "--verbose", help="Verbose output", action="store_true", default=False)
    args = ap.parse_args()
    
    copyProject(args.outputPath, args)
