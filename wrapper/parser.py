#!/usr/local/bin/env python3
import argparse
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("ImagePath", help="Path to image")

args = ap.parse_args()

print("Image path: " + args.ImagePath)


image = Image.open(args.ImagePath)
#image = image.filter(ImageFilter.FIND_EDGES)
#image.save('newImage.png')

image = image.convert('RGB')

pixels = image.load()
width, height = image.size


print(width)
print(height)
print(pixels)
mydict = []
number = 0
dictionary = {}

for x in range(0, height):
    for y in range(0, width):
        r,g,b = image.getpixel((y, x))
        print(r,g,b, "    ", x, y)
        if (r and g and b != 255):
            try:
                dictionary[r,g,b].append((x,y))
            except KeyError:
                dictionary[r,g,b] = [(x,y)]
            print("heello")
            myitem = (x, y, " ", r,g,b)
            mydict.append(myitem)
            number += 1

    print(" ")


#print(mydict)
print(dictionary)
print(number)

print(len(dictionary))



print("Done")
