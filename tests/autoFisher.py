'''
Auto Fisher
Michael Gorbunov

This program afk-fishes via Python script. Uses xdotools and likely only works on linux.

Heavily base on Justinyugit's script (also the inspiration for this entire project)
https://github.com/justinyugit/mini-projects/blob/master/OpenCV-AutoFishBot/run.py
'''

import numpy as np
from PIL import Image
import time
import cv2
import mss
import os


def get_mouse_pos ():
    # pos_str = ['x:123', 'y:1232', ...]
    pos_str = os.popen("xdotool getmouselocation").read().split(" ")
    mouse_x = int(pos_str[0][2:])
    mouse_y = int(pos_str[1][2:])

    return [mouse_x, mouse_y]


def get_mouse_locale ():
    '''Takes a picture around the mouse and returns it'''
    sq_size = 200
    sct = mss.mss()
    mouse_pos = get_mouse_pos()

    #We capture a square above the mos_pos
    top = mouse_pos[1] - sq_size
    left = mouse_pos[0] - sq_size // 2
    monitor = {"top": top, "left": left, "width": sq_size, "height": sq_size}
    img = Image.frombytes("RGB", (sq_size, sq_size), sct.grab(monitor).rgb)
    IMG = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    return IMG


def process_image (image):
    '''Processes the image and returns the image'''
    lower = np.array([36, 36, 189], dtype="uint8")
    upper = np.array([48, 48, 229], dtype="uint8")

    return cv2.inRange(image, lower, upper)


# Start
tot_time = 7
fps = 30
cur_time = tot_time
while (cur_time >= 0):
    img = get_mouse_locale()
    if (cur_time < 3):
        img = cv2.putText(
            img,
            "Starting in 3 sec",
            (10, 100),
            cv2.QT_FONT_NORMAL,
            0.6,
            (130, 120, 210),
            1
        )


    cv2.imshow('test', img)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        exit()

    delay = 1 / fps
    cur_time -= delay
    time.sleep(delay)


# Main loop
while (True):
    img = process_image(get_mouse_locale())
    cv2.imshow('test', img)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

    if np.sum(img) == 0:
        os.system("xdotool click 3")
        time.sleep(1)
        os.system("xdotool click 3")
        time.sleep(5)
        continue


