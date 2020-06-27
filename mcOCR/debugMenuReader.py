import numpy as np
import OCRReader as read
import cv2
from PIL import Image
import os
import time


og_img = cv2.imread("Debugmenu.png")
og_img = og_img[:500, :800]

text = read.read_image(og_img)
print(text)


cv2.destroyAllWindows()

