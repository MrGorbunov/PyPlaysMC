import numpy as np
import OCRReader as read
import cv2
from PIL import Image
import os
import time


input_img = cv2.imread("Debugmenu.png")
input_img = input_img[:500, :800]

text = read.read_image(input_img)
print(text)

print("Now trying to cache")
y_to_save = read.get_line_y(input_img, "XYZ")
print(y_to_save)
print(read.read_at_line_y(input_img, y_to_save))


cv2.destroyAllWindows()

