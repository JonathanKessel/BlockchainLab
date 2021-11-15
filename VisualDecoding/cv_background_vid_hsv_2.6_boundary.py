# Funktioniert super bei statischem Hintergrund ist für unseren use Case aber so noch nicht zu gebrauchen.
# Diese Version implementiert die Kombination aus Supervised und Unsupervised Learning
# trying to set the diver boundaries automatically
# counting difference in bounding box pixels and non bounding box pixels of splash
# implemented multiple bounding boxes to be used
# added confidence threshold of 50% to find splash start.
########### DEVELOPMENT FINISHED --> FINAL VERSION OF CODE ###############


from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
from collections import defaultdict
import json


def extract_hsv_info(splash_frame, dict_all_bounding_boxes, pct1, pct2):
    cap = cv.VideoCapture("209.mp4")
    cap.set(1, splash_frame - 3)
    ret, frame = cap.read()

    # get relevant frame
    boxes_dict = dict_all_bounding_boxes[splash_frame]

    # converts the BGR color space of image to HSV color space
    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    # Getting x,y coordinates from diver and extracting diver
    diver_dict = boxes_dict["diver"]
    # unpacking coordinates
    ymin, ymax = int(diver_dict["ymin"]), int(diver_dict["ymax"])
    xmin, xmax = int(diver_dict["xmin"]), int(diver_dict["xmax"])

    diver_extract = hsv_frame[ymin: ymax,
                    xmin:xmax]
    diver_extract_rgb = frame[ymin:ymax,
                        xmin:xmax]
    # We know that we have a diver against a blue colored background -> remove most of the blue color
    # (hMin = 0 , sMin = 0, vMin = 0), (hMax = 179 , sMax = 88, vMax = 255)
    lower_range_diver = np.array([0, 22, 75])
    upper_range_diver = np.array([16, 95, 177])

    # preparing the mask to overlay
    mask_diver = cv.inRange(diver_extract, lower_range_diver, upper_range_diver)

    # The black region in the mask has the value of 0,
    # so when multiplied with original image removes all non-blue regions
    result_diver = cv.bitwise_and(diver_extract_rgb, diver_extract_rgb, mask=mask_diver)

    result_diver = cv.cvtColor(result_diver, cv.COLOR_BGR2HSV)

    # Storing color information for each pixel in a dictionary
    colour_dict = defaultdict(list)
    # result_diver -> (a, b, c) color_value; a,b == x, y; c -> hue/saturation/value
    # going through the result diver
    for index, y in np.ndenumerate(result_diver):
        # print(index, y)
        # getting current
        colour_info = result_diver[index[0]][index[1]][index[2]]
        # print(colour_info)
        # saving the color information with the pixels as keys in the color dictionary
        colour_dict[index[0], index[1]].append(colour_info)

    # list with h, s, v for statistical analysis
    hue = []
    saturation = []
    value_x = []
    # removing colour info [0, 0, 0]
    for key, value in colour_dict.copy().items():
        # removing black pixels
        # print("value: ", value)
        if value == [0, 0, 0] or value == [0, 255, 0]:
            # print("found")
            colour_dict.pop(key)
        else:
            # print(key, value)
            hue.append(value[0])
            saturation.append(value[1])
            value_x.append(value[2])

    hmin, hmax = np.percentile(hue, [pct1, pct2])
    smin, smax = np.percentile(saturation, [pct1, pct2])
    vmin, vmax = np.percentile(value_x, [pct1, pct2])

    # set lower boundaries by algo and upper values manually
    lower_range_diver = np.array([hmin, smin, vmin])
    upper_range_diver = np.array([np.float64(80), np.float64(255), np.float64(255)])
    return lower_range_diver, upper_range_diver


"Importing and reading info on bounding boxes"
# Reading JSON with bounding info from Supervised Learning
# file = open("./_tigfCJFLZg_00206_predictions.json")
file = open("./_tigfCJFLZg_00209_predictions.json")
all_bounding_boxes_dict = json.load(file)
data1 = {}
# removing leading zeroes from key(s)
for key, value in all_bounding_boxes_dict.items():
    data1[int(key)] = value
all_bounding_boxes_dict = data1

# get moment at which we see splash for the first time
for key, value in all_bounding_boxes_dict.items():
    # do we have a splash with a score of at least x.
    if "splash0" in value and float(value["splash0"]["score"]) > 0.5:
        # save the current key and use it to render splash
        splash_frame = int(key)
        print("plash frame:", splash_frame)
        # exiting loop, otherwise we will set the splash frame to the last frame with a splash
        break

"--- START OPENCV --"
parser = argparse.ArgumentParser(description='This program shows how to use background subtraction methods provided by \
                                              OpenCV. You can process both videos and images.')
parser.add_argument('--input', type=str, help='Path to a video or a sequence of image.', default='209.mp4')
parser.add_argument('--algo', type=str, help='Background subtraction method (KNN, MOG2).', default='MOG2')
args = parser.parse_args()
if args.algo == 'MOG2':
    backSub = cv.createBackgroundSubtractorMOG2(varThreshold=200)
else:
    backSub = cv.createBackgroundSubtractorKNN()
capture = cv.VideoCapture(cv.samples.findFileOrKeep(args.input))
capture_2a = cv.VideoCapture('./Ergebnisse/2a_no_mog2.mp4')
if not capture.isOpened():
    print('Unable to open: ' + args.input)
    exit(0)

# get the length of the video
length = int(capture.get(cv.CAP_PROP_FRAME_COUNT))
print("num frames", length)
frame_count = 0

# using Color extractor to get colours.
lower_range_diver, upper_range_diver = extract_hsv_info(splash_frame, all_bounding_boxes_dict, 1, 95)
print("ranges lower: ", lower_range_diver, "ranges upper: ", upper_range_diver)
out_stack = cv.VideoWriter('./Ergebnisse/2b_stack_boundaries.mp4', cv.VideoWriter_fourcc('m', 'p', '4', 'v'), 10.0, (2080, 480))
capture_2b = cv.VideoCapture('./Ergebnisse/2b_mask.mp4')

while True:
    ret_2b, frame_2b = capture_2b.read()
    if frame_count == length - 1:
        break
    print("frame: ", frame_count)
    frame_count += 1
    if frame_count == 32:
        print("hi")

    """--- DIVER ONLY PART BEGIN ---"""
    "grab bounding box info from dictionary"
    # acces dictionary by frame / key
    boxes_dict = all_bounding_boxes_dict[frame_count]

    # Do we have a splash this frame?
    # intizializing dict with all splashes
    splash_dict = {}
    if "splash0" in boxes_dict:
        boxes_ymax = []

        for key in boxes_dict:

            # get ymax only for splash boxex
            if key == 'diver':
                continue
            # extracting ymax for current splash
            ymax_in_box = boxes_dict[key]['ymax']
            # appending current splash
            boxes_ymax.append(ymax_in_box)
            # saving all splashes of frame in splash dict
            splash_dict[key] = boxes_dict[key]

        # get max y from all splash boxes of one frame    
        maxy_splash = max(boxes_ymax)

    ret_2a, frame_2a = capture_2a.read()
    ret, frame = capture.read()
    # converts the BGR color space of image to HSV color space
    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    "Focusing on bounding Box @Diver"
    # checking if we have a diver in the dict
    diver_check = False

    if "diver" in boxes_dict:
        diver_check = True
        # Getting x,y coordinates from diver and extracting diver
        diver_dict = boxes_dict["diver"]
        # unpacking coordinates
        ymin, ymax = int(diver_dict["ymin"]), int(diver_dict["ymax"])
        xmin, xmax = int(diver_dict["xmin"]), int(diver_dict["xmax"])

        diver_extract = hsv_frame[ymin: ymax,
                        xmin:xmax]
        diver_extract_rgb = frame[ymin:ymax,
                            xmin:xmax]

        diver_extract = cv.GaussianBlur(diver_extract, (5, 5), 0)
        diver_extract_rgb = cv.GaussianBlur(diver_extract_rgb, (5, 5), 0)

        diver_extract_gray = cv.cvtColor(diver_extract_rgb, cv.COLOR_BGR2GRAY)
        black_extract = np.zeros(diver_extract_gray.shape)
        cv.imshow('gray', diver_extract_gray)
        "Getting contours and removing areas that are too small "
        # getting contours
        ret, thresh = cv.threshold(diver_extract_gray, 125, 200, 0)
        contours, hierarchy = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
        # cv.drawContours(diver_extract_rgb.copy(), contours, -1, (0, 255, 0), 1)

        result_diver_hsv = cv.cvtColor(diver_extract_rgb, cv.COLOR_BGR2HSV)
        # focusing on contours that are white
        intensities = []
        # for each list of contour points...
        # 255 -> black; 127 white
        for i in range(len(contours)):
            cv.drawContours(diver_extract, contours, -1, (0, 255, 255), 1)
            # focusing on contours that are white
            # we are only interested in contours large enough
            # Create a mask image that contains the contour filled in
            cimg = np.zeros_like(diver_extract)
            # filling contours into "cimg".
            cv.drawContours(cimg, contours, i, color=255, thickness=-1)
            # cv.imshow('cimg', cimg)
            # access the contour and count the number of white pixels within.
            n_pxs = np.count_nonzero(cimg == 255)
            # getting points of relevant pixels.
            pts = np.where(cimg == 255)
            # if we have less than x pixels, we make those pixels black in the mask and result frame.
            if n_pxs < 150:
                # cv.drawContours(black_extract, contours, i, color=0, thickness=-1)
                cv.drawContours(frame, contours, i, color=0, thickness=-1)
            else:
                # -> more than x number of n_pxs -> we use the contour to colour the area white.
                #  --> we dont want white on areas that are black -> "non diver areas"
                # checking if the area within the contour is black -> we dont want those in the mask.
                # accessing intensities.
                # saving color infos from relevant pts / pxs
                intensities.append(result_diver_hsv[pts[0], pts[1]])
                cv.drawContours(black_extract, contours, i, color=255, thickness=-1)
                # getting mean intensity
                for cnt in intensities:
                    mean0 = np.mean(cnt, axis=0)

        "Putting the ROI of the diver back onto a Canvas with the result / mask shape"
        # creating black result ([0, 0, 0]) to overlay the actual result-> (640, 480, 3),
        black_result = np.full((480, 640, 3), [0, 0, 0])
        # making sure it is HSV
        black_result = np.float32(black_result)
        black_result = cv.cvtColor(black_result, cv.COLOR_BGR2HSV)
        # inserting the modified result into the black canvas
        diver_extract = cv.cvtColor(diver_extract, cv.COLOR_HSV2BGR)
        black_result[ymin:ymax, xmin:xmax] = diver_extract

        # set black result as result diver
        result_diver = black_result

        # creating black mask
        black_mask = np.zeros((480, 640))
        # inserting mask into black mask
        black_mask_ROI = black_mask[ymin:ymax, xmin:xmax]
        black_mask[ymin:ymax, xmin:xmax] = black_extract

        # setting black mask as mask
        mask_diver_no_MOG2 = black_mask
        # print(mask_diver_no_MOG2.shape)
        "--- DIVER ONLY PART END ---"

    "Creating boundaries"
    # left boundary, currently yellow
    result_diver[0:480, 0:150] = [0, 255, 255]
    # right boundary, currently yellow
    result_diver[0:480, 550:680] = [0, 255, 255]
    # top boundary, currently yellow
    result_diver[0:50, 0:680] = [0, 255, 255]

    if "diver" in boxes_dict:
        # Converting the Diver Mask to HSV Colorspace: GRAY2BGR -> BGR2HSV
        mask_diver_no_MOG2 = np.float32(mask_diver_no_MOG2)
        mask_diver_no_MOG2 = cv.cvtColor(mask_diver_no_MOG2, cv.COLOR_GRAY2BGR)
        mask_diver_no_MOG2 = cv.cvtColor(mask_diver_no_MOG2, cv.COLOR_BGR2HSV)

        # print("Mask diver bgr: ", mask_diver_no_MOG2.shape)
        # White Pixels now red, coloring them white again.
        # --> find all pixels with [0, 0, 255] make them[255, 255, 255]
        mask_diver_no_MOG2[np.where((mask_diver_no_MOG2 == [0, 0, 255]).all(axis=2))] = [0, 255, 255]  # (!!!)
        # left boundary, currently black
        mask_diver_no_MOG2[0:480, 0:150] = [0, 0, 0]
        # right boundary, currently black
        mask_diver_no_MOG2[0:480, 550:680] = [0, 0, 0]
        # top boundary, currently black
        mask_diver_no_MOG2[0:50, 0:680] = [0, 0, 0]

    # Applying MOG2 Algorithm.
    mask_diver = backSub.apply(result_diver)

    # Saving a Grayscale Image to color the white pxs later.
    mask_diver_gray = mask_diver.copy()
    # Make filtered Diver Yellow
    # Converting the Diver Mask to HSV Colorspace: GRAY2RGB -> RGB2HSV
    mask_diver = np.float32(mask_diver)
    mask_diver = cv.cvtColor(mask_diver, cv.COLOR_GRAY2BGR)
    # print("Mask diver bgr: ", mask_diver.shape)
    mask_diver = cv.cvtColor(mask_diver, cv.COLOR_BGR2HSV)
    # White Pixels now red, coloring them white again.
    # --> find all pixels with [0, 0, 255] make them[0, 0, 0]
    mask_diver[np.where((mask_diver == [0, 0, 255]).all(axis=2))] = [255, 255, 255]
    # now get all pixels from diver mask and color them yellow.
    mask_diver[np.where((mask_diver_gray == [255]))] = [0, 255, 255]

    "Color Filter Splash"
    # wir wollen den splash Algo erst gegen Ende zuschalten.
    # Initializing splash as False -> "off"
    splash = False
    # do we have a splash?
    if "splash0" in boxes_dict:
        # print("SPLASH")
        # "activating" Splash
        splash = True
        # It converts the BGR color space of image to HSV color space
        hsv_splash = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        # Threshold HSV space for diver/everything -> (hMin = 0 , sMin = 0, vMin = 0),
        #                                               (hMax = 179 , sMax = 104, vMax = 255)
        # Diver HSV -> np.array([0, 42, 105]) ; np.array([60, 80, 255])
        # Splash HSV -> [109, 0, 198]; [255, 255, 255]
        lower_range_splash = np.array([109, 0, 220])
        upper_range_splash = np.array([255, 255, 255])

        # preparing the mask to overlay
        mask_splash = cv.inRange(hsv_splash, lower_range_splash, upper_range_splash)

        # Diver und Splash farblich trennen.

        # The black region in the mask has the value of 0,
        # so when multiplied with original image removes all non-blue regions
        result_splash = cv.bitwise_and(frame, frame, mask=mask_splash)

        # Count pixels of Splash
        pixels = cv.countNonZero(mask_splash)
        total_count = 0
        for key, value in splash_dict.items():
            cnt_in_bx = cv.countNonZero(mask_splash[int(splash_dict[key]["ymin"]): int(splash_dict[key]["ymax"]),
                                        int(splash_dict[key]["xmin"]):int(splash_dict[key]["xmax"])])
            total_count += cnt_in_bx

        # Make Splash Red.
        # Converting the Mask to HSV Colorspace: GRAY2RGB -> RGB2HSV
        # White becomes red through GRAY -> BGR -> HSV transformation.
        mask_splash = cv.cvtColor(mask_splash, cv.COLOR_GRAY2BGR)
        mask_splash = cv.cvtColor(mask_splash, cv.COLOR_BGR2HSV)
        "Color Filter Splash --end--"
    # Do we have splash? -> See initalization above.
    # Make mask_diver mask to main_mask, will be overwritten if we have a splash and a diver mask.
    main_mask = mask_diver
    main_result = result_diver

    # print("shape: ", main_mask.shape)
    cv.rectangle(main_result, (10, 2), (100, 20), (255, 255, 255), -1)
    cv.putText(main_result, "Frames:" + str(capture.get(cv.CAP_PROP_POS_FRAMES)), (10, 20),
               cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
    if frame_count == 100:
        cv.imwrite("./209_frame100.jpg", frame)

    if splash:
        # stitching the two masks together (diver and splash) if we have both.
        # Overwriting main mask and result
        if frame_count == 180:
            cv.imwrite(filename="./splash.jpg", img=result_splash)
        main_mask = mask_splash + mask_diver
        main_result = result_splash + result_diver
        mask_diver_no_MOG2 = mask_diver_no_MOG2 + mask_splash
        # adding borders where we dont have splash according to supervised info
        main_result[int(maxy_splash): 480, 0:640] = [0, 255, 255]
        main_mask[int(maxy_splash): 480, 0:640] = [0, 0, 0]
        mask_diver_no_MOG2[int(maxy_splash): 480, 0:640] = [0, 0, 0]

        # Showing number of Splash Pixels absolute and % (if Splash present)
        # adding white Box to make text readable
        # left boundary, currently yellow
        main_result[25:100, 15:250] = [255, 255, 255]
        cv.putText(main_result, "Pixels:" + str(pixels), (20, 35),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
        # Calc number of splash pxs as %
        pct_pxs = round((pixels / 307200) * 100, 2)
        cv.putText(main_result, "Pixels %:" + str(pct_pxs), (20, 50),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

        cv.putText(main_result, "Pixel count in Box:" + str(total_count), (20, 65),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
        cv.putText(main_result, "Count diff :" + str(pixels - total_count), (20, 80),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
        cv.putText(main_result, "(unsup pixels - bb pixels)", (20, 95),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))



    else:
        cv.putText(main_result, "No Splash", (20, 40),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
    "drawing bounding box from supervised algo"
    cv.rectangle(main_result, (xmin, ymin),
                 (xmax, ymax), (255, 255, 0), 1)
    cv.putText(main_result, 'diver', (xmin, ymin - 10), cv.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 0))

    # TODO -> Draw bounding boxes for all existing splashes!
    for key, value in splash_dict.items():
        cv.rectangle(main_result, (int(splash_dict[key]["xmin"]), int(splash_dict[key]["ymin"])),
                     (int(splash_dict[key]["xmax"]), int(splash_dict[key]["ymax"])), (0, 255, 255), 1)
        cv.putText(main_result, 'splash', (int(splash_dict[key]["xmin"]), int(splash_dict[key]["ymin"]) - 10),
                   cv.FONT_HERSHEY_SIMPLEX, 0.2, (0, 255, 255))

    # {'xmin': '19', 'ymin': '253', 'xmax': '39', 'ymax': '286'}

    main_result = main_result.astype(np.uint8)
    cv.imshow('main result', main_result)
    cv.imshow('FG Mask', main_mask)
    cv.imshow('original frame', frame)
    cv.imshow('no MOG2 mask', mask_diver_no_MOG2)
    # cv.imshow("diver", diver_extract)

    print(mask_diver_no_MOG2.shape)
    mask_diver_no_MOG2 = mask_diver_no_MOG2.astype('uint8')
    mask_diver_no_MOG2_small = mask_diver_no_MOG2[0:480, 150:550]
    """
     mask_diver_no_MOG2[0:480, 0:150] = [0, 0, 0]
        # right boundary, currently black
        mask_diver_no_MOG2[0:480, 550:680] = [0, 0, 0]
        # top boundary, currently black
        mask_diver_no_MOG2[0:50, 0:680] = [0, 0, 0]
    """
    stack = cv.hconcat([frame_2b, mask_diver_no_MOG2_small, main_result, frame])
    print(stack.shape)
    out_stack.write(stack)
    cv.imshow('stack', stack)
    if frame_count == 149:
        cv.imwrite('./Ergebnisse/Splash Quantification/result.jpg', main_result)
        cv.imwrite('./Ergebnisse/Splash Quantification/no_mog2_mask.jpg', mask_diver_no_MOG2_small)


    keyboard = cv.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        pass
        break
