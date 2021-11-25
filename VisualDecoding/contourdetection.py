# Standard imports
import cv2
import numpy as np

im = cv2.imread('example_small.png')
imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
cv2.imwrite("gray_img.jpg", imgray)
imgray = cv2.blur(imgray, (10, 10))
cv2.imwrite("blur.jpg", imgray)
ret, thresh = cv2.threshold(imgray, 50, 255, 0)


#tresh = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(im, contours, -1, (0, 255, 0), 3)
print(len(contours))
cv2.imwrite("result.jpg", im)