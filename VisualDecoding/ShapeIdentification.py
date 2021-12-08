import numpy as np
import cv2
from copy import deepcopy

img = cv2.imread("middletection-extract_img.jpg")
imgGry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
image_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(image_hsv, (0, 0, 150), (255, 255, 255))
cv2.imwrite("shapedetection-mask.jpg", mask)
imgGry = cv2.blur(imgGry, (10, 10))

contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
img_copy = img.copy()
img_copy = cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 3)
cv2.imwrite("shapedetection-contours.jpg", img_copy)

# removing noise
cnt_copy = []
for cnt in contours:
    size = cv2.contourArea(cnt)
    if size > 500:
        cnt_copy.append(cnt)
        print(size)

contours = cnt_copy
img_copy = img.copy()
img_copy = cv2.drawContours(img_copy, cnt_copy, -1, (0, 255, 0), 3)
cv2.imwrite("shapedetection-rel-contours.jpg", img_copy)

for contour in contours:
    # find the corners of contours, True because contours are closed
    peri = cv2.arcLength(contour, True)
    print("peri: ", peri)
    # gets number of points and position(?)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    points = len(approx)
    x, y, w, h = cv2.boundingRect(approx)
    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 5)
    img = cv2.putText(img, "Points: " + str(points), (x + w + 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 255))
    # we have a rectangle
    if len(approx) == 4:
        img = cv2.putText(img, "rectangle", (x + w + 15, y + 15), cv2.FONT_HERSHEY_SIMPLEX, .5,
                          (0, 255, 255))
    if len(approx) == 3:
        img = cv2.putText(img, "triangle", (x + w + 15, y + 15), cv2.FONT_HERSHEY_SIMPLEX, .5,
                          (0, 255, 255))
        #TODO Figuring out which direction the traingle is facing by investigating the points
    if len(approx) > 4:
        img = cv2.putText(img, "circle", (x + w + 15, y + 15), cv2.FONT_HERSHEY_SIMPLEX, .5,
                          (0, 255, 255))



cv2.imwrite("shapedetection-info.jpg", img)
