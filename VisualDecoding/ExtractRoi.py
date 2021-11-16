import cv2
import numpy as np

im = cv2.imread('Handy_Bild_3.jpg')
print(im.shape)
imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
imgray = cv2.blur(imgray, (10, 10))

# Ansammlung von Symbolen -> 36 Symbole
# Alle ca in der mitte des bildes
# 24 weiß, 12 farbig
# Alle ca gleich groß

# remove 20% above and below pic


ret, thresh = cv2.threshold(imgray, 50, 255, 0)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(im, contours, -1, (0, 255, 0), 3)
cv2.imwrite("result.jpg", im)

