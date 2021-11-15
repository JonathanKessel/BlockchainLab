import cv2
import numpy as np
import json

# get colorcodes from json
file = open("./ColorCoding.json")
colorInfo = json.load(file)
converted_info = dict()
# converted_info -> {0: {"lower": (), "upper":(), "name":"xyyzz"}, 1: {"lower": (), "upper":(), "name":"xyyzz"}}
for key, value in colorInfo.items():
    converted_info[value["name"]] = {"lower": (value["lower-hsv"]["hue"], value["lower-hsv"]["saturation"],
                           value["lower-hsv"]["value"]),
                           "upper": (value["upper-hsv"]["hue"], value["upper-hsv"]["saturation"],
                                     value["upper-hsv"]["value"]),
                           "value": key}
#loading image
im = cv2.imread('example_small.png')
image_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
# Running contour detection on picture 
imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray, 50, 255, 0)
cv2.imwrite("gray_img.jpg", imgray)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# cv2.drawContours(im, contours, -1, (0, 255, 0), 3)
# Initialize empty list
lst_intensities = []
colored_contour_coords = []
print("number of contours: ", len(contours))
# For each list of contour points...
for i in range(len(contours)):
    print("curr contour: ", i, "of", len(contours))
    # Create a mask image that contains the contour filled in
    cimg = np.zeros_like(imgray)
    cv2.drawContours(cimg, contours, i, color=255, thickness=-1)
    # Access the image pixels and create a 1D numpy array then add to list
    # pts = koordinaten der aktuellen kontour
    pts = np.where(cimg == 255)
    lst_intensities.append(image_hsv[pts[0], pts[1]])
    # is this a white contour?
    avg_color = np.mean(contours[i], axis = 0)
    if avg_color[0] + avg_color[1] > 150:
        colored_contour_coords.append(pts)

# identify non-white contours
contour_color = []
colored_contours = []
for contour in lst_intensities:
    contour_color.append(np.mean(contour, axis = 0))

for contour in contour_color:
    if contour[0] + contour[1] > 150:
        colored_contours.append(contour)

# paint colored contours onto mask to extract code
mask = np.zeros_like(image_hsv)



cv2.imwrite("intensities_im.jpg", im)
cv2.imwrite("intensities_imgra.jpg", imgray)
