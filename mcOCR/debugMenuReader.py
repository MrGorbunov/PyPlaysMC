import numpy as np
import cv2
from PIL import Image
import os
import time


img = cv2.imread("Debugmenu.png")
img = img[:500, :800]

# The text on is always at r,g,b = 221
lower = (219, 219, 219)
upper = (224, 224, 224)
img = cv2.inRange(img, lower, upper)

'''
Get histogram along vertical
 > each gap is a line break

along each line, get a histogram
 > each gap is a letter

We now have information about the line gaps (vertical) and letter gaps (horizontal)
and can make bounding boxes to segment the image.
'''

#
# Get vertical histogram
#

'''
[  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0... 
[  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0...
[  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0...
[  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0...
[  0,   0,   0,   0, 255, 255,   0,   0,   0,   0,   0,   0...
[  0,   0,   0,   0, 255, 255,   0,   0,   0,   0,   0,   0...
[  0,   0,   0,   0, 255, 255, 255, 255,   0,   0, 255, 255...
[  0,   0,   0,   0, 255, 255, 255, 255,   0,   0, 255, 255...
[  0,   0,   0,   0, 255, 255,   0,   0, 255, 255,   0,   0...
[  0,   0,   0,   0, 255, 255,   0,   0, 255, 255,   0,   0...
[  0,   0,   0,   0, 255, 255,   0,   0,   0,   0,   0,   0...

This is what the top left of the image looks like currently.
To find the start of the M, we go diagonally from the top left
pixel until we hit white.
'''

y1 = 0
while img[y1, y1] == 0:
    y1 += 1

y2 = y1
while img[y2, y1] == 255:
    # since top left of M is diagnol from top, y1 is also an x-cord
    y2 += 1

line_height = y2 - y1
if line_height != 14:
    if line_height < 14:
        print("Error: Wrong gui scale, too small")
    elif line_height > 14:
        print("Error: Wrong gui scale, too big")

    input()
    exit(0)


height, width = img.shape
img = cv2.resize(img, (width // 2, height // 2), interpolation=cv2.INTER_NEAREST)
height, width = img.shape

y1 //= 2
line_height //= 2
cur_y = 0
x_values = [y1, y1+1, y1+2, y1+3, y1+4, y1+5]
prev_white = False

# Max gap of pixels
max_gap = 30

# Hold bboxes of text regions
text_regions = []


cv2.imshow('test', img)
cv2.waitKey(0)

while cur_y < height:
    # We try to find the bottom of lines by essentially
    # raycasting. At multiple x values, we go down and once
    # (A or B or C) goes from 1 -> 0, we hit the bottom of line
    is_white = False
    for x in x_values:
        if img[cur_y, x] > 0:
            is_white = True
            break

    if not is_white and prev_white:
        # Bottom pixel of line is cur_y - 1, now lets scan horizontally

        # These are left n right bounds for letter
        left_x = x_values[0]
        right_x = left_x
        prev_slice = False

        for right_x in range(0, width - 1):
            if right_x - left_x > max_gap:
                break

            white_in_slice = False
            for y in range(cur_y - line_height, cur_y):
                # img = cv2.circle(img, (x_values[-1] + 4, y), 1, (150, 150, 150))
                if img[y, right_x] > 0:
                    white_in_slice = True
                    break

            if not white_in_slice and prev_slice:
                # x1, x2, y1, y2
                text_regions += [[left_x, right_x, cur_y - line_height, cur_y+1]]

            if white_in_slice and not prev_slice:
                left_x = right_x

            prev_slice = white_in_slice


    prev_white = is_white
    cur_y += 1




import OCRReader as read
text = read.read_bboxes(img, text_regions)
print(text)


cv2.destroyAllWindows()

