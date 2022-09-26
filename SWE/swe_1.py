import os

import argparse
import cv2
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--f', dest = 'folder', type=str, required=True, help='Folder with images')
args = parser.parse_args()


if not os.path.exists(args.folder):
    raise Exception('Folder does not exist')

# RGB Format, lower and upper bounds for red and blue
red = [(200,0,0),(255,20,20)] 
blue = [(0,0,200),(20,20,255)]
color_array = [blue, red]

position = [] # array of [filename, y, x]
count = 0
total_files = len(os.listdir(args.folder))
for filename in os.listdir(args.folder):
    if not filename.endswith(".jpg"):
        continue
    result = [filename]
    img = cv2.imread(os.path.join(args.folder, filename))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if count == 0:
        h,w,c = img.shape

    for colour in [blue, red]:
        lower = colour[0]
        upper = colour[1]

        img_copy = img.copy()
        mask = cv2.inRange(img_copy,lower,upper) # Mask for the color
        # img= cv2.medianBlur(img, 3)
        mask = cv2.resize(mask, None, fx = 2, fy = 2, interpolation = cv2.INTER_CUBIC)


        contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contour_list = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
            area = cv2.contourArea(contour)
            if ((len(approx) > 8) & (area > 30) ):
                contour_list.append(contour)
        result.append(len(contour_list))
        # cv2.drawContours(mask, contour_list,  -1, (255,0,0), 2)

    if len(result) == 3:
        position.append(result)
        count += 1

print("Total files: ", total_files)
print("Number of images: ", count)
if total_files != count:
    raise Exception('Number of images does not match')
# print(position)

# ASSUMPTION, each image has the same dimensions
if count:
    max_y = max([x[1] for x in position])
    max_x = max([x[2] for x in position])
    vis = np.zeros((max_y*h, max_x*w, 3), np.uint8)

    for filename, y, x in position:
        img = cv2.imread(os.path.join(args.folder, filename))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        vis[(y-1)*h:y*h, (x-1)*w:x*w] = img

    # Save file
    import re
    vis_file = re.split('/|\\\\',args.folder)[-1] + ".jpg"
    cv2.imwrite(vis_file, vis)
    plt.imshow(vis)
    plt.show()
