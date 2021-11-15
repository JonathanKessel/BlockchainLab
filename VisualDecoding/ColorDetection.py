import cv2
import numpy as np
import json

def round_it(num):
    l = len(str(num)) - 1
    rounded = round(num / 10.0 ** l)
    rounded = int(rounded * 10 ** l)
    return rounded

def bubblesort(arr):
    n = len(arr)

    # Traverse through all array elements
    for i in range(n - 1):
        # range(n) also work but outer loop will repeat one time more than needed.
        #curr_i = arr[i]
        #print(curr_i)
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            curr_j = arr[j]
            # print(curr_j)
            # traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            # compare x coordinates, if it is to the right -> higher number
            if arr[j]["coods"][0] > arr[j + 1]["coods"][0]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
            # if its to the left compare height (y coordinate)
                # if its below -> higher number
            else:
                if arr[j]["coods"][1] > arr[j + 1]["coods"][1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

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
    print("curr contour: ", i, "of", len(contours) -1)
    # Create a mask image that contains the contour filled in
    cimg = np.zeros_like(imgray)
    cv2.drawContours(cimg, contours, i, color=255, thickness=-1)
    # Access the image pixels and create a 1D numpy array then add to list
    # pts = koordinaten der aktuellen kontour
    pts = np.where(cimg == 255)
    lst_intensities.append(image_hsv[pts[0], pts[1]])
    # is this a white contour?
    # calculate mean color values
    avg_color = np.mean(lst_intensities[i], axis = 0)
    # check if the sum of first to colums is larger than 150
    if avg_color[0] + avg_color[1] > 150:
        # saving each symbol
        filename = str(i) + "-symbol.jpg"
        cv2.imwrite(filename, cimg)
        # if so keep the coords of that symbol
        colored_contour_coords.append(pts)

print("anzahl farbiger symbole", len(colored_contour_coords))
contour_pos = []
l = 0

for contour in colored_contour_coords:
    avg_y = round_it(np.mean(contour[0]))
    avg_x = round_it(np.mean(contour[1]))
    contour_pos.append({"coods": (avg_x, avg_y), "pos": l})
    l += 1

    ordered_pos = bubblesort(contour_pos)

print("tatdaaa")
cv2.imwrite("intensities_im.jpg", im)
cv2.imwrite("intensities_imgra.jpg", imgray)
