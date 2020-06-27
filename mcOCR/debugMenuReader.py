import numpy as np
import OCRReader as read
import cv2
from PIL import Image
import os
import time


input_img = cv2.imread("Debugmenu.png")
input_img = input_img[:500, :800]


print("Now trying to cache")
y_to_save = read.get_line_y(input_img, "XYZ")
print(y_to_save)
# print(read.read_at_line_y(input_img, y_to_save))

# The following nums are averages of 5 runs
# 100 iterations of read_image = 6.667 sec
# _1000_ iterations of read_at_line_y = 3.914 sec
# 
# Caching the line y and reading with it it is ~17x faster
print("Now to get some metrics")
iterations = 1000
start_time = time.time()

for i in range(iterations):
    read.read_at_line_y(input_img, y_to_save)
tot_time = start_time - time.time()

print(tot_time)

cv2.destroyAllWindows()

