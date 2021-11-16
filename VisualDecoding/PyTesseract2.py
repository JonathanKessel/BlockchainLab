import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = cv2.imread('Handy_Bild_3.jpg')

data = pytesseract.image_to_data(img, output_type='dict')
boxes = len(data['level'])
for i in range(boxes ):
    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
    #Draw box
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

# search for the keywords [ART, BLOCKCHAIN, HDM, STUTTGART]

cv2.imwrite('img2.jpg', img)
