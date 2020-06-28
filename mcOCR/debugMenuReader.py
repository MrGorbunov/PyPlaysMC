import numpy as np
import OCRReader as read
import cv2
from PIL import Image
import os
import time
import mss
import screenCalibrater as sC


# The following nums are averages of 5 runs
# 100 iterations of read_image = 6.667 sec
# _1000_ iterations of read_at_line_y = 3.914 sec
# 
# Caching the line y and reading with it it is ~17x faster

monitor = sC.get_window_monitor()
width = monitor["width"]
height = monitor["height"]

print("Now sleeping for 1")

time.sleep(1)
print("OK lets do this")

sct = mss.mss()
input_img = Image.frombytes("RGB", (width, height), sct.grab(monitor).rgb)
input_img = cv2.cvtColor(np.array(input_img), cv2.COLOR_RGB2BGR)
input_img = input_img[:, :800]


def extract_numbers (text: str):
    # Regex would be cleaner, but this is simple enough
    # to be hopefully more efficient

    # text = XYZ.###/###/###
    num_strings = []
    left_ind = 0
    first_dot = True
    for ind, char in enumerate(text):
        if first_dot and char == '.':
            left_ind = ind + 1
            first_dot = False

        elif char == '/':
            num_strings += [text[left_ind:ind]]
            left_ind = ind + 1
    num_strings += [text[left_ind:]]    

    nums = []
    for string in num_strings:
        nums += [float(string)]

    return nums

y_to_save = read.get_line_y(input_img, "XYZ")
text = read.read_at_line_y(input_img, y_to_save)
print(text)
coords = extract_numbers(text)
print(coords)



while 1:
    input_img = Image.frombytes("RGB", (width, height), sct.grab(monitor).rgb)
    input_img = cv2.cvtColor(np.array(input_img), cv2.COLOR_RGB2BGR)
    input_img = input_img[:, :800]
    text = read.read_at_line_y(input_img, y_to_save)
    coords = extract_numbers(text)
    print("X: {0}  Y: {1}   Z: {2}".format(coords[0], coords[1], coords[2]))

    

    time.sleep(0.1)



