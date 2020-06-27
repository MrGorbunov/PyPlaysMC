import numpy as np
import cv2
from PIL import Image
import mss
import os
import time


'''
Move to one corner of mc

Move to opposite corner of mc
'''

img = np.zeros((300, 300, 3), dtype="uint8")

# Display countdown
for i in range(7)[::-1]:
    img = np.zeros((300, 300, 3), dtype="uint8")
    img = cv2.putText(img, str(i+1), (100, 170), cv2.FONT_HERSHEY_DUPLEX, 3, (150, 200, 250), 1)
    cv2.imshow('test', img)

    cv2.waitKey(1)
    time.sleep(1)

img = np.zeros((300, 300, 3), dtype="uint8")
img = cv2.putText(img, "Go", (100, 170), cv2.FONT_HERSHEY_DUPLEX, 3, (150, 200, 250), 1)
cv2.waitKey(1)


# Now get screen cords
def get_mouse_pos ():
    # pos_str = ['x:123', 'y:1232', ...]
    pos_str = os.popen("xdotool getmouselocation").read().split(" ")
    mouse_x = int(pos_str[0][2:])
    mouse_y = int(pos_str[1][2:])

    return [mouse_x, mouse_y]

def get_mouse_locale (sq_size: int):
    '''Takes a picture around the mouse and returns it'''
    sct = mss.mss()
    mouse_pos = get_mouse_pos()

    #We capture a square above the mos_pos
    top = mouse_pos[1] - sq_size
    left = mouse_pos[0] - sq_size // 2
    monitor = {"top": top, "left": left, "width": sq_size, "height": sq_size}
    IMG = Image.frombytes("RGB", (sq_size, sq_size), sct.grab(monitor).rgb)
    IMG = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    return IMG


sct = mss.mss()

#Window position on screen
x_max, y_max = -1, -1
x_min, y_min = 100000, 100000

tot_time = 10
fps = 30
cur_time = tot_time
delta = 1 / fps

while cur_time >= 0:
    #Mouse position logic
    mouse_loc = get_mouse_pos()
    mouse_x = mouse_loc[0]
    mouse_y = mouse_loc[1]

    if mouse_x < x_min:
        x_min = mouse_x
    elif mouse_x > x_max:
        x_max = mouse_x
    if mouse_y < y_min:
        y_min = mouse_y
    elif mouse_y > y_max:
        y_max = mouse_y

    print("mn: " + str(x_min) + "    mx:" + str(x_max))
    #Rendering for clarity
    if (y_max - y_min > 10 and x_max - x_min > 10):
        height = y_max - y_min
        width = x_max - x_min
        scale_factor = 0.4

        monitor = {"top": y_min, "left": x_min, "height": height, "width": width}
        img = Image.frombytes("RGB", (width, height), sct.grab(monitor).rgb)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        IMG = cv2.resize(img, (int(width * scale_factor), int(height * scale_factor)), interpolation=cv2.INTER_CUBIC)

        cv2.imshow('test', IMG)
        cv2.waitKey(1)

    cur_time -= delta
    time.sleep(delta)

cv2.imwrite("DebugTrickScreenshot.png", img)
cv2.waitKey(0)

