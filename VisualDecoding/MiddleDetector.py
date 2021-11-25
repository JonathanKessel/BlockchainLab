import numpy as np
import cv2

img = cv2. imread('IMG_5683 - small.png')

# approximate the middle of the picture
h, w, c = img.shape
print(h, w, c)
# look for contours in the pic
imgGry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
imgGry = cv2.blur(imgGry, (10, 10))
cv2.imwrite('middle-gray.jpg', imgGry)
# ret, thresh = cv2.threshold(imgGry, 0, 255, cv2.THRESH_TRUNC)
ret, thresh = cv2.adaptiveThreshold(imgGry)
cv2.imwrite("threshold.jpg", thresh)
contours, hierarchy = cv2.findContours(imgGry, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
imsave = img.copy()
cv2.drawContours(imsave, contours, -1, (0, 255, 0), 3)
cv2.imwrite("middletection.jpg", imsave)



#identify those in the middle of the pic



# look for more symbols that have about the same distance than the ones we already discovered