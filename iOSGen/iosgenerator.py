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


listenM = {}
listenMP = {}
listenH = {}

def copyProject(outputPath, debug, args):
    newListeM = []
    newListeH = []
    newListeMP = []
    configSetup()
    
    #Project does not exsist, create a new one
    if not os.path.exists(outputPath):
        fromDirectory = "DemoApp"
        copy_tree(fromDirectory, outputPath)
        viewName = input("Enter a name for the new view: ")
        os.rename(outputPath + "/DemoApp/ViewControllerBase.h", outputPath + "/DemoApp/" + viewName + "Base.h")
        os.rename(outputPath + "/DemoApp/ViewControllerBase.m", outputPath + "/DemoApp/" + viewName + "Base.m")
        os.rename(outputPath + "/DemoApp/ViewController.m", outputPath + "/DemoApp/" + viewName + ".m")
        os.rename(outputPath + "/DemoApp/ViewController.h", outputPath + "/DemoApp/" + viewName + ".h")

    #Project already exists, check that all files are present
    else:
        print("You say that you want to change an existing project. Checking for files and stuff...")


    with open(args.jsonPath) as data_file:
        data = OrderedDict()
        try:
            data = json.load(data_file, object_pairs_hook=OrderedDict)
        except ValueError:
            print(Fore.RED + "Something went wrong. Could not read JSON. Is the JSON structure correct?" + Style.RESET_ALL)
            return

        for e in data.items():
            if e[0] != "meta":
                readElement(e[1][1], newListeM, newListeH, newListeMP)
    if debug: print("Done parsing the JSON elements")

    replaceText(outputPath, "m", viewName, newListeM, newListeMP)
    replaceText(outputPath, "h", viewName, newListeH, None)

    print(Fore.GREEN + "iOS generator done" + Fore.RESET)


def configSetup():
    Config = configparser.RawConfigParser()
    Config.read("colorTypes.ini")
    readConfigFile(Config)

def readConfigFile(config):
    options1 = config.options("implementationsFields")
    for option in options1:
        listenM["#" + option] = eval(config.get("implementationsFields", option))

    options2 = config.options("addingFields")
    for option in options2:
        if str(option) == 'default':
            listenMP[option] = eval(config.get("addingFields", option))
        else:
            listenMP["#" + option] = eval(config.get("addingFields", option))
    options3 = config.options("headerFields")
    for option in options3:
        listenH["#" + option] = eval(config.get("headerFields", option))


#Return (red, green, blue) for the color given as #rrggbb.
def hex_to_rgb(value):
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
            if ("POSX" in item[0]):
                newItem = str(newItem).replace("POSX", str(posX))
            if ("POSY" in item[0]):
                newItem = str(newItem).replace("POSY", str(posY))
            if ("WIDTH" in item[0]):
                newItem = str(newItem).replace("WIDTH", str(width))
            if ("HEIGHT" in item[0]):
                newItem = str(newItem).replace("HEIGHT", str(height))
            if ("COLOR" in item[0]):
                (r,g,b) = hex_to_rgb(color)
                rgbColor = "colorWithRed:{0}/255.0 green:{1}/255.0 blue:{2}/255.0 alpha:1".format(r,g,b)
                newItem = str(newItem).replace("COLOR", rgbColor) 
            newListeM.append(newItem)
    else:
        print(Fore.RED + color + " - is not a valid color and will be ignored" + Style.RESET_ALL
        	+"\nRead the documentation to add your own colors and corresponding elements.")

def saveIOSobjectH(color, elementId, listenH, newListeH):
    if(color in listenH):
        name = listenH[color][0][0] + str(elementId)
        headerElement = listenH[color][1][0]
        newItem = str(headerElement).replace("NAME", str(name))
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

    if len(contentStructure) > 0:
        for i in range (0, len(contentStructure)):
            readElement(contentStructure[str(i)][1], newListeM, newListeH, newListeMP)
      

def replaceText(templatePath, fileType, filename, elements, elements2):
    templatePath = templatePath+"/DemoApp"
    file1 = open(templatePath + "/" + filename + "Base." + fileType , "r")
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

    file3 = open(templatePath + "/" + filename + "Base." + fileType , "w")
    file4 = open(templatePath + "/NewFile.txt", "r")

    for line in file4:
        file3.write(line)

    file3.close()
    file4.close()

    if(os.path.exists(templatePath + '/NewFile.txt')):
        os.remove(templatePath + '/NewFile.txt')

if __name__== "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonPath", help="Path to JSON structure") #NB! Vi kan også bruke styles her! :)
    ap.add_argument("outputPath", help="Output directory")
    ap.add_argument("-v", "--verbose", help="Verbose output", action="store_true", default=False)
    args = ap.parse_args()
    
    copyProject(args.outputPath, args.verbose, args)
