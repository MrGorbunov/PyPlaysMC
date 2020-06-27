import numpy as np
from mss import mss
from PIL import Image
import cv2


# ======== Getting Screencaps from the game =======
# sct = mss()
#
# w, h = 400, 400
# monitor = {"top": 30, "left": 30, "width": w, "height": h}
#
# while (True):
#     img = Image.frombytes("RGB", (w, h), sct.grab(monitor).rgb)
#     IMG = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
#     if cv2.waitKey(25) & 0xFF == ord('q'):
#         cv2.destroyAllWindows()
#         break


# ====== Testing Processing on Screen Cap ======
# IMG = cv2.imread("GameScreenShot.png", cv2.IMREAD_COLOR)
# IMG = cv2.line(IMG, (10, 10), (300, 300), (71, 146, 232), 2)
# IMG = cv2.rectangle(IMG, (10, 10), (300, 300), (232, 146, 71), 2)
#
#
# cv2.imshow('test', IMG)
#
# while (True):
#     if cv2.waitKey(0) & 0xFF == ord('q'):
#         cv2.destroyAllWindows()
#         break


img = cv2.imread("GameScreenShot.png")
window_name = "Filtering Testing"
cv2.namedWindow(window_name)

# Select central region
width, height, _ = img.shape
center_w = width // 2
center_h = height // 2
sq_size = 200
# Because it goes +- in both directions
sq_size //= 2

center_img = img[(center_w - sq_size):(center_w + sq_size), (center_h - sq_size):(center_h + sq_size)]


while (True):
    cv2.imshow(window_name, center_img)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
