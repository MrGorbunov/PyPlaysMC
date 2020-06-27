import os
import time


def get_into_mc ():
    '''
    Will make the window active and remove the escape menu.
    Requires the cursor to be above the mc window.
    '''
    os.system("xdotool click 1")
    os.system("xdotool keydown Escape")



# ===== Walk forward for 5 seconds =====
# get_into_mc()
# os.system("xdotool keydown w")
# time.sleep(5)
# os.system("xdotool keyup w")


# ===== Turn right =====
# For some reason, this does not work in mc 1.15.2
# os.system("xdotool mousemove_relative --sync 100 10")
# time.sleep(1)
# os.system("xdotool mousemove_relative --sync 100 10")
# time.sleep(.5)


# ===== Scraping the image =====



