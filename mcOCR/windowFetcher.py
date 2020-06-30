'''
Window Fetcher

These functions will find the dimensions of the Minecraft
window and also take screen caps.
'''

import os
import time
import numpy as np
import cv2
from PIL import Image
from mss import mss



'''
            Small General Funcs
'''
def get_mouse_pos ():
    '''Returns system mouse position, as [x,y] pair'''
    # pos_str = ['x:123', 'y:1232', ...]
    pos_str = os.popen("xdotool getmouselocation").read().split(" ")
    mouse_x = int(pos_str[0][2:])
    mouse_y = int(pos_str[1][2:])

    return [mouse_x, mouse_y]

def get_mouse_locale (sq_size: int):
    '''Takes a picture around the mouse and returns it'''
    sct = mss()
    mouse_pos = get_mouse_pos()

    top = mouse_pos[1] - sq_size // 2
    left = mouse_pos[0] - sq_size // 2
    monitor = {"top": top, "left": left, "width": sq_size, "height": sq_size}
    IMG = Image.frombytes("RGB", (sq_size, sq_size), sct.grab(monitor).rgb)
    IMG = cv2.cvtColor(np.array(IMG), cv2.COLOR_RGB2BGR)

    return IMG

def capture_area (monitor_dict):
    sct = mss()
    IMG = Image.frombytes("RGB", 
                          (monitor_dict["width"], monitor_dict["height"]),
                          sct.grab(monitor_dict).rgb)
    IMG = cv2.cvtColor(np.array(IMG), cv2.COLOR_RGB2BGR)
    return IMG




'''
            Window Capturing

This is a multi-second sequence wherein the bounds
of the Minecraft window are captured. It works by 
tracking the min & max x & y of the mouse while the
person moves their mouse to the two corners. Minecraft
bounds the mouse position so this is easy.
'''
def display_countdown (duration: int):
    '''
    Displays a countdown on the screen
    duration = # seconds, must be int
    '''
    # For some reason the first digit doesn't show without this
    img = np.zeros((300, 300, 3), dtype="uint8")
    cv2.imshow('test', img)
    cv2.waitKey(1)

    for i in range(duration)[::-1]:
        img = np.zeros((300, 300, 3), dtype="uint8")
        img = cv2.putText(img, str(i+1), (100, 170),
                          cv2.FONT_HERSHEY_DUPLEX, 3,
                          (150, 200, 250), 1)

        cv2.imshow('test', img)
        cv2.waitKey(1)
        time.sleep(1)

def preview_current_bounds (x_min, x_max, y_min, y_max, time_left, scale_factor):
    min_dimension = min(y_max - y_min, x_max - x_min)

    if min_dimension > 10:
        height = y_max - y_min
        width = x_max - x_min

        monitor = {"top": y_min, "left": x_min, "height": height, "width": width}
        sct = mss()
        img = Image.frombytes("RGB", (width, height), sct.grab(monitor).rgb)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img = cv2.resize(img, 
                         (int(width * scale_factor), int(height * scale_factor)), 
                         interpolation=cv2.INTER_CUBIC)

        bot_left = ( 10, int(height * scale_factor) - 10)
        img = cv2.putText(img, str((time_left * 10) // 1 / 10.0), 
                          bot_left, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 200, 250))

        cv2.imshow('test', img)
        cv2.waitKey(1)

    else:
        img = np.zeros((300, 300, 3), dtype="uint8")
        img = cv2.putText(img, "Move that mouse!", (50, 170),
                          cv2.FONT_HERSHEY_DUPLEX, 0.6,
                          (150, 200, 250), 1)

        cv2.imshow('test', img)
        cv2.waitKey(1)

def get_window_dimensions (duration: int, fps: int):
    '''
    Provides duration seconds for the player to move the cursor
    and capture the corners of the MC window. Refreshes at
    the supplied frames per second.

    Returns a monitor dict; top, left, height, width
    '''
    delta = 1.0 / fps
    time_left = duration

    x_max, y_max = -1, -1
    # If a monitor is more than 100,000 px wide then that's straight wack
    x_min, y_min = 100000, 100000

    while time_left >= 0:
        mouse_x, mouse_y = get_mouse_pos()

        if mouse_x < x_min:
            x_min = mouse_x
        elif mouse_x > x_max:
            x_max = mouse_x
        if mouse_y < y_min:
            y_min = mouse_y
        elif mouse_y > y_max:
            y_max = mouse_y

        preview_current_bounds(x_min, x_max, y_min, y_max, time_left, 0.3)

        time_left -= delta
        time.sleep(delta)


    return {"top": y_min, "left": x_min, "height": y_max - y_min, "width": x_max - x_min}

