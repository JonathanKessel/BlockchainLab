import cv2
import numpy as np
import json

# get colorcodes from json
file = open("./ColorCoding.json")
colorInfo = json.load(file)
converted_info = dict()
# converted_info -> {0: {"lower": (), "upper":(), "name":"xyyzz"}, 1: {"lower": (), "upper":(), "name":"xyyzz"}}
for key, value in colorInfo.items():
    converted_info[key] = {"lower": (value["lower-hsv"]["hue"], value["lower-hsv"]["saturation"],

                                     value["lower-hsv"]["value"]),
                           "upper": (value["lower-hsv"]["hue"], value["lower-hsv"]["saturation"])}

print(converted_info)
