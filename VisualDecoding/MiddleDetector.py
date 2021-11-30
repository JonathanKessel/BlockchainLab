"""
THIS IS PSEUDOCODE
1. Get all contours
2. Cluster all contours based on the following Information: Distance to next contour, size, position
        Distance -> shortest distance to the next contour by iterating over every contour distance.
3. Get those 36 Objects that are closest in that cluster and more or less in the middle
"""
import cv2
import numpy as np
import math
from sklearn.cluster import DBSCAN
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import Birch
from sklearn.cluster import ward_tree
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import MeanShift
from sklearn.cluster import KMeans
import pandas as pd
import math
import seaborn as sns
from statistics import mean


img = cv2. imread('IMG_5685_1.png')
# img = cv2. imread('example_block-2.png')

# approximate the middle of the picture
h, w, c = img.shape
print(h, w, c)
# convert to gray and blur pic
imgGry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
imgGry = cv2.blur(imgGry, (10, 10))
image_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.imwrite('middle-gray.jpg', imgGry)
# using a mask instead of thresholding since a mask is more reliable
# ret, thresh = cv2.threshold(imgGry, 100, 255, 0)
# thresh = cv2.adaptiveThreshold(imgGry, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 10, 10)
mask = cv2.inRange(image_hsv, (0, 0, 185), (255, 255, 255))

# ret, thresh = cv2.threshold(imgGry, 50, 255, 0)
cv2.imwrite("mask.jpg", mask)

# get contours
contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
imsave = img.copy()
cv2.drawContours(imsave, contours, -1, (0, 255, 0), 3)
cv2.imwrite("middletection.jpg", imsave)

cnt_inf = {}
# c: {size: xx, pos: (xxx, yyy), dst_next_cnt: xxx}
lst_intensities = []
# Saving pixels of each contour in coords_cnts
# coords_cnts = {contour_key: [[x_values], [y_values]]}
coords_cnts = {}
for i in range(len(contours)):
    print("curr contour: ", i, "of", len(contours) - 1)
    # Create a mask image that contains the contour filled in
    cimg = np.zeros_like(imgGry)
    cv2.drawContours(cimg, contours, i, color=255, thickness=-1)
    # Access the image pixels and create a 1D numpy array then add to list
    # pts = coordinates of the contour
    pts = np.where(cimg == 255)
    avg_y = np.mean(pts[0])
    avg_x = np.mean(pts[1])
    cnt_size = len(pts[0])
    # saving x_y coords of each contour for later
    coords_cnts[i] = [[], []]
    coords_cnts[i][0] = pts[1]
    coords_cnts[i][1] = pts[0]
    lst_intensities.append(image_hsv[pts[0], pts[1]])
    # is this a white contour?
    # calculate mean color values
    avg_color = np.mean(lst_intensities[i], axis=0)
    if avg_color[2] > 100:
        # we dont want really small contours since they are usually noise and we expect
        # a somewhat large picture
        if cnt_size > 50:
            # we save the avg position and size of each contour, the distance to next contour will be added shortly
            # this dictionary will be used throughout the code to access the contours
            cnt_inf[i] = {"size": cnt_size, "pos": (avg_x, avg_y), "dst_next_cnt": None}

# saving relevant contours for visiualizing
rel_contours = []
rel_img = img.copy()
for key, info in cnt_inf.items():
    rel_contours.append(contours[key])
cv2.drawContours(rel_img, contours, -1, (0, 255, 0), 3)
cv2.imwrite("rel-contours.jpg", rel_img)


# Compute distances from each contour to each contour and get shortest dist
# first loop to iterate over cnt_inf items
for i, info in cnt_inf.items():
    # dictionary to save all distances between i and n. Will be redeclared as soon as i is increased
    distances = []
    x_y_i = info["pos"]
    # secon loop to compare against the first loop
    for n, info2 in cnt_inf.items():
        # we dont want to compare n against i since they are the same and the distance would be zero
        if i != n:
            # grabbing coordinates and computing the distance
            x_y_n = info2["pos"]
            x_dist = (x_y_i[0] - x_y_n[0])**2
            y_dist = (x_y_i[1] - x_y_n[1])**2
            curr_distance = math.sqrt(x_dist + y_dist)
            # saving the distance measured between n and i
            distances.append(curr_distance)
    # find shortest distance
    shortest_dist = min(distances)
    # save the shortest distance
    cnt_inf[i]["dst_next_cnt"] = shortest_dist
    print("cnt: ", i, "info:", info)


cnt_inf_list = []
for key, info in cnt_inf.items():
    pos_x = info["pos"][0]
    pos_y = info["pos"][1]
    size = info["size"]
    dist = info["dst_next_cnt"]
    cnt_inf_list.append([pos_x, pos_y, size, dist])

df = pd.DataFrame(cnt_inf_list, columns=["pos_x", "pos_y", "size", "dst_next_cnt"])
pd.set_option('display.max_rows', 1000)

sorted_df = df.sort_values(by=["pos_x"])

df2 = df[["pos_x", "pos_y"]]
X = df2.to_numpy()
"""
f1 = sorted_df[sorted_df['y_pos'] > 2000]
f2 = f1[f1['y_pos'] < 5000]
f3 = f2[f2['dst_next_cnt'] > 200]
print(f2)
"""
print(sorted_df)


"""
CLUSTERING -- BEGINNING
"""
cluster_model = Birch()
labels_clustering = cluster_model.fit_predict(X)
print(labels_clustering)

i = 0
for key, cntr in cnt_inf.items():
    cnt_inf[key]["labels_clustering"] = labels_clustering[i]
    i += 1

"""
CLUSTERING -- END
"""

"""
DECIDING WHICH CLUSTER TO CHOOSE based on the distance to the middle -> Middle doesnt work that well 
at least in current implementation -> better would be by 
"""
# center -> (x, y)
center = (w/2, h/2)
# clusters
n_cluster = len(np.unique(labels_clustering))
unique_cluster = np.unique(labels_clustering)
# calculating center of each cluster
x_y_cluster = [[], []]
x_y_mean = {}
closest_distance = None
closest_cluster = None
for cluster in unique_cluster:
    for key, value in cnt_inf.items():
        if value["labels_clustering"] == cluster:
            # append x and y values
            x_y_cluster[0].append(value["pos"][0])
            x_y_cluster[1].append(value["pos"][1])
    # calculate avg distance to center from a cluster
    mean_x = mean(x_y_cluster[0])
    mean_y = mean(x_y_cluster[1])
    #curr_distance = math.sqrt(((center[0] - mean(x_y_cluster[0]))**2) - (center[1] - )**2))
    xplusy = ((center[0] - mean_x) ** 2) + ((center[0] - mean_y) ** 2)
    curr_distance = math.sqrt(xplusy)

    x_y_mean[cluster] = curr_distance
# get cluster that is closest to the center
i = 0
for key, cluster in x_y_mean.items():
    # first element we dont want to compare
    if i == 0:
        closest_distance = cluster
        closest_cluster = key
    else:
        if closest_distance > cluster:
            closest_distance = cluster
            closest_cluster = key
print(closest_cluster)

"""
Assuming we have successfully selected the right cluster all the distances should be about equal on the 
correct symbols, we make sure and check the distance and eliminate those that are too far appart / close together
"""




"""
Extract max upper left and bottom right avg points for the closest cluster, get original contours and 
extract image subset
"""
# x_y_cluster -> {key: {pos: (x, y), distance: xxx}}
x_y_cluster = {}
# iterate over cnt_inf and extract values for cluster 2
for key, value in cnt_inf.items():
    if value["labels_clustering"] == closest_cluster:
        # append x and y values
        x_y_cluster[key] = {"pos": None, "distance": None}
        x_y_cluster[key]["pos"] = value["pos"]
        x_y_cluster[key]["distance"] = math.sqrt((0 - value["pos"][0])**2 + (0 - value["pos"][1])**2)


upper_left_distance = None
lower_right_distance = None
upper_left_key = None
lower_right_key = None
i = 0
# get the key for upper right and lower left
for key, value in x_y_cluster.items():
    # look for upper left and lower right by checking distance
    # initializing values
    if i == 0:
        upper_left_distance = value["distance"]
        lower_right_distance = value["distance"]
        upper_left_key = key
        lower_right_key = key
        i += 1
    # looking for a smaller distance -> new upper left
    if upper_left_distance > value["distance"]:
        upper_left_distance = value["distance"]
        upper_left_key = key
    # looking for a bigger distance -> new lower right
    if lower_right_distance < value["distance"]:
        lower_right_distance = value["distance"]
        lower_right_key = key

print("upper_left", cnt_inf[upper_left_key])
print("lower_right", cnt_inf[lower_right_key])
# go into original contours and retrieve by key
upper_left_cords = min(coords_cnts[upper_left_key][0]), min(coords_cnts[upper_left_key][1])
lower_right_cords = max(coords_cnts[lower_right_key][0]), max(coords_cnts[lower_right_key][1])
print("true upper left: ", upper_left_cords)
print("true lower right: ", lower_right_cords)
# add cushion based on contour size
sizes = []
for key, cnt in cnt_inf.items():
    sizes.append(cnt["size"])
cushion = mean(sizes) * 0.012
print(cushion)
upper_left_cushion = (int(upper_left_cords[0] - cushion), int(upper_left_cords[1] - cushion))
lower_right_cushion = (int(lower_right_cords[0] + cushion), int(lower_right_cords[1] + cushion))

# extract subimage
extract_img = img[upper_left_cushion[1]:lower_right_cushion[1],
                  upper_left_cushion[0]:lower_right_cushion[0]]

cv2.imwrite("extract_img.jpg", extract_img)

"""VISUALIZING --- BEGINNING"""
palette = sns.color_palette("husl", n_cluster)
palette_RGB = []
for color in palette:
    rgb0, rbg1, rgb2 = color[0]*255, color[1]*255, color[2]*255
    palette_RGB.append((rgb0, rbg1, rgb2))

imgColor = np.zeros((h, w, 3), np.uint8)
for key, info in cnt_inf.items():
    # print("key: ", key)
    imgColor = cv2.putText(imgColor, str(round(info["dst_next_cnt"])),
                           (int(info["pos"][0]) + 50, int(info["pos"][1]) + 50), cv2.FONT_HERSHEY_SIMPLEX, 3,
                           (0, 255, 0), 20, cv2.LINE_AA)

    imgColor = cv2.putText(imgColor, str(round(info["size"])),
                           (int(info["pos"][0]) - 50, int(info["pos"][1]) - 50), cv2.FONT_HERSHEY_SIMPLEX, 3,
                           (0, 255, 0), 20, cv2.LINE_AA)
    color_rgb = palette_RGB[info["labels_clustering"]]

    imgColor = cv2.circle(imgColor, (int(info["pos"][0]), int(info["pos"][1])), radius=20,
                          color=color_rgb, thickness=-1)

cv2.imwrite("result_middle2.jpg", imgColor)



