'''
Char Code Maker

This program takes in the AllCharacters image, the
flags, and produces character codes. The flags are 
coordinates that point to black / white places. These
are essnetially bit flags, and so stringing them
together gets a number. This is the char code.

In practice, the image will be searched at the flags
and the resulting code will be looked up. This program
thus produces a dict of char code -> character. Also,
the characters are divided by width, so it ends up
being a dict of dicts (look at OCRConstants.py).

Last point, there's a lot of reuse from OCRFlagMaker.
'''

from OCRConstants import flags_dict
import math
import numpy as np
import cv2



'''
           Display Funcs
'''
def display_at_scale (img, scale_factor, display_text=""):
    temp_img = img.copy()

    w, h = 0, 0

    try:
        w, h = temp_img.shape
    except:
        # Color images
        w, h, _ = temp_img.shape

    temp_img = cv2.resize(temp_img,
                          (h * scale_factor, w * scale_factor),
                          interpolation=cv2.INTER_NEAREST)

    if display_text != "":
        # If this is a grayscale image, the rgb code converts to a dark gray
        cv2.putText(temp_img, display_text, (0, temp_img.shape[0]-3), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 160, 65), thickness=2)

    cv2.imshow('test', temp_img)
    cv2.waitKey(0)

def display_with_bboxes (img, bboxes, color=(150, 250, 200), scale_factor=4):
    display_copy = img.copy()
    w, h = display_copy.shape
    display_copy = cv2.resize(display_copy,
                              (h * scale_factor, w * scale_factor),
                              interpolation=cv2.INTER_NEAREST)
    display_copy = cv2.cvtColor(display_copy, cv2.COLOR_GRAY2RGB)

    for bbox in bboxes:
        display_copy = cv2.rectangle(display_copy,
                                     (bbox[0] * scale_factor, bbox[2] * scale_factor), 
                                     (bbox[1] * scale_factor, bbox[3] * scale_factor),
                                     (150, 250, 200))

    display_at_scale(display_copy, 1)

def display_flags_over_image (img, bboxes, flags):
    '''Displays flags'''
    use_img = img.copy()
    scale_fac = 2

    w, h = use_img.shape
    use_img = cv2.resize(use_img, (h*scale_fac, w*scale_fac), interpolation=cv2.INTER_NEAREST)
    use_img = cv2.cvtColor(use_img, cv2.COLOR_GRAY2RGB)

    for bbox in bboxes:
        x, y = bbox[0] * scale_fac, bbox[3] * scale_fac

        for flag in flags:
            x_off = flag[0]*scale_fac
            y_off = flag[1]*scale_fac
            use_img = cv2.circle(use_img,
                                 (x + x_off, y + y_off),
                                 0,
                                 (150, 250, 100))

    display_at_scale(use_img, 2)
    


'''
           Pre Processing
'''
char_img = cv2.imread("AllCharacters.png")
char_img = cv2.inRange(char_img, (250, 250, 250), (255, 255, 255))

# Makes text 1-px thick
height, width = char_img.shape
char_img = cv2.resize(char_img, (width // 2, height // 2), interpolation=cv2.INTER_NEAREST)
height, width = char_img.shape

display_at_scale(char_img, 4)






'''
           Scanning for characters
'''
line_height = 8

first_x = 6
first_y = 12
second_y = 21


def scan_line_for_chars (img, start_x, start_y):
    '''Using x,y as the bottom left corner, it will scan the line and return new char bboxes'''
    global line_height, width

    return_bboxes = []
    left_x = start_x
    prev_white_slice = False

    for x in range(start_x, width):
        is_white_slice = False
        for y in range(start_y - line_height, start_y):
            if img[y, x] > 0:
                is_white_slice = True
                break

        # Reached end of character
        if prev_white_slice and not is_white_slice:
            return_bboxes += [[left_x, x, start_y, start_y - line_height]]

        # Reached start of character
        if not prev_white_slice and is_white_slice:
            left_x = x

        prev_white_slice = is_white_slice

    return return_bboxes

char_bboxes = []
char_bboxes += scan_line_for_chars(char_img, first_x, first_y)
char_bboxes += scan_line_for_chars(char_img, first_x, second_y)

display_with_bboxes(char_img, char_bboxes)






'''
           Generating Char Codes
'''
def calc_char_code (img, bbox, flags):
    '''This is constructing a binary number'''
    return_val = 0
    for flag in flags:
        return_val *= 2

        # bbox gives cords for origin, flag gives offset
        x = bbox[0] + flag[0]
        y = bbox[3] + flag[1]
        px_val = img[y, x]

        if px_val > 100:
            return_val += 1
    
    return return_val


chars_dict = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
# these match the image and also the order of the char_bboxes
chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890' \
        '!@#$%^&*()-_=+~[{}]:;"\'<>,.?/\\|'

for ind, bbox in enumerate(char_bboxes):
    key = bbox[1] - bbox[0]

    print("now doing :" + chars[ind])
    flags = flags_dict[key]
    val = calc_char_code(char_img, bbox, flags)
    chars_dict[key][chars[ind]] = val




'''
            Reversing the Dict

Now we have a dict of char -> char_code but for usage
we want it to be char_code -> char.
'''
final_char_dict = {}

for key in chars_dict.keys():
    final_char_dict[key] = {}

    for char in chars_dict[key].keys():
        code = chars_dict[key][char]
        final_char_dict[key][code] = char


for key in final_char_dict.keys():
    print(final_char_dict[key])
    print('')




