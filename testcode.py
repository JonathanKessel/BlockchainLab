import cv2
import numpy as np

# read image
img = cv2.imread("doco3.jpg")

# convert img to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# do adaptive threshold on gray image
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 101, 3)

# apply morphology open then close
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
blob = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9,9))
blob = cv2.morphologyEx(blob, cv2.MORPH_CLOSE, kernel)

# invert blob
blob = (255 - blob)

# Get contours
cnts = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
big_contour = max(cnts, key=cv2.contourArea)

# test blob size
blob_area_thresh = 1000
blob_area = cv2.contourArea(big_contour)
if blob_area < blob_area_thresh:
    print("Blob Is Too Small")

# draw contour
result = img.copy()
cv2.drawContours(result, [big_contour], -1, (0,0,255), 1)

# write results to disk
cv2.imwrite("doco3_threshold.jpg", thresh)
cv2.imwrite("doco3_blob.jpg", blob)
cv2.imwrite("doco3_contour.jpg", result)

# display it
cv2.imshow("IMAGE", img)
cv2.imshow("THRESHOLD", thresh)
cv2.imshow("BLOB", blob)
cv2.imshow("RESULT", result)
cv2.waitKey(0)
