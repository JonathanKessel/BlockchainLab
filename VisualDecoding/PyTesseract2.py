import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = cv2.imread('Handy_Bild_3.jpg')
image_width, image_heigt, image_channels = img.shape
data = pytesseract.image_to_data(img, output_type='dict')
boxes = len(data['level'])
"""
for i in range(boxes ):
    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
    #Draw box
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
"""

# search for the keywords [ART, BLOCKCHAIN, HDM, STUTTGART]
# words -> [] mit einträgen {coords : [(xmin, ymin), (xmax, ymax)]}, word: "string"}
words = []
i = 0
for text in data["text"]:
    if text == "BLOCKCHAIN" or text == "ART" or text == "HDM" or text == "STUTTGART" or text == "LAB":
        xmin = data["left"][i]
        ymin = data["top"][i]
        xmax = data["left"][i] + data['width'][i]
        ymax = data["top"][i] + data['height'][i]
        words.append({"coords": [(xmin, ymin), (xmax, ymax)], "text": text})
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
    i += 1

# get relevant positional information
# get highest y value
ymax = 0
for text in words:
    # look through all text parts with "Blockchain" 
    if text["text"] == "BLOCKCHAIN":
        if ymax < text["coords"][0][1]:
            pass


cv2.imwrite('img2.jpg', img)



