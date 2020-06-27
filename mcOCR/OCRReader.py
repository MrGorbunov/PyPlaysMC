'''
OCR Reader

This is the bad boi that does it all.
'''
# TODO: Seperate out the debugging (display) funcs into 
#       their own script - same with CharCodeMaker and FlagMaker

import math
import numpy as np
import cv2


'''
           Display Funcs

These funcs aren't used by the calls but
are useful for debugging
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

def display_with_line (img, line_cord, horiz=True, scale_factor=3):
    display_img = img.copy()
    
    dims = img.shape
    h, w = dims[:2]
    display_img = cv2.resize(display_img, 
        (w * scale_factor, h * scale_factor), 
        interpolation=cv2.INTER_NEAREST)

    line_cord *= scale_factor
    p1, p2 = 0, 0
    if horiz:
        p1 = (0, line_cord)
        p2 = (len(display_img[0]), line_cord)
    else:
        p1 = (line_cord, 0)
        p2 = (line_cord, len(display_img))
    display_img = cv2.line(display_img, p1, p2, (150, 150, 150))

    display_at_scale(display_img, 1)

def display_many_lines (img, line_cords, horiz=True, scale_factor=3):
    display_img = img.copy()
    
    dims = img.shape
    h, w = dims[:2]
    display_img = cv2.resize(display_img, 
        (w * scale_factor, h * scale_factor), 
        interpolation=cv2.INTER_NEAREST)

    for cord in line_cords:
        cord *= scale_factor
        p1, p2 = 0, 0
        if horiz:
            p1 = (0, cord)
            p2 = (len(display_img[0]), cord)
        else:
            p1 = (cord, 0)
            p2 = (cord, len(display_img))
        display_img = cv2.line(display_img, p1, p2, (150, 150, 150))

    display_at_scale(display_img, 1)

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





'''
            Reading Images
'''
# TODO: figure out how to declare return types in python
def read_image (color_img):
    '''
    Reads the text in a screenshot of mc
    Is returned with newlines between lines, but no spaces
    
    Preconditions:
        All text is inline - cannot tolerate multiple vertically offset textboxes
        Correct GUI scale - text must be 2 pixels thick coming in
        Color - text color must be (221, 221, 221)
        Minimal low-hanging letters - too many g, y, j, 3,, will break it (sorry)
    '''
    text_img = isolate_debug_text(color_img)
    text_img = resize_text_img(text_img)
    bboxes = extract_char_bboxes(text_img)

    ret_text = ""
    for line_bboxes in bboxes:
        ret_text += read_bboxes(text_img, line_bboxes)
        ret_text += '\n'
    ret_text = ret_text[:-1]

    return ret_text

def isolate_debug_text (color_img):
    # The text is at r,g,b = 221
    lower = (219, 219, 219)
    upper = (224, 224, 224)
    img = cv2.inRange(color_img, lower, upper)
    return img

# TODO: Detect the thickness of the text automatically
def resize_text_img (text_img):
    h, w = text_img.shape
    # Right now I'm assuming the text is 2 px thick
    text_img = cv2.resize(text_img, (w//2, h//2), interpolation=cv2.INTER_NEAREST)
    return text_img





# TODO: this should be a or part of a class
'''
            ROI Creation and Caching

Right now I only care about xyz/ coordinate info. Since
that's only part of the screen I can cache that part and
then repeated calls will come to it.
'''
def get_line_y (color_img, search_text):
    '''
    Returns the y of the first line which contains text verbatim
    Same preconditions as read_text
    If nothing is found, -1 is returned
    '''
    text_img = isolate_debug_text(color_img)
    text_img = resize_text_img(text_img)

    #TODO: here there are unnecessary calls because 
    #      extract_char_bboxes also calls get_baselines
    bboxes = extract_char_bboxes(text_img)
    line_ys = get_baselines(text_img)

    for index, line_bboxes in enumerate(bboxes):
        line_text = read_bboxes(text_img, line_bboxes)

        if search_text in line_text:
            return line_ys[index]

    return -1

def read_at_line_y (color_img, line_y):
    text_img = isolate_debug_text(color_img)
    text_img = resize_text_img(text_img)
    line_bboxes = extract_bboxes_in_line(text_img, line_y)
    return read_bboxes(text_img, line_bboxes)

    





'''
            Reading Characters
'''
# These constants are generated by OCRFlagMaker and OCRCharCodeMaker

# key = character width
flags_dict = {
    1: [[0,1],[0,0],[0,7],[0,3]],
    2: [[0,0]],
    3: [[1,2],[0,2]],
    4: [[1,1],[1,4],[0,2],[2,2]],
    5: [[1,1],[0,4],[3,3],[2,4],[4,4],[4,6],[0,0],[1,0],[4,0],[1,5],[3,2],[0,2]],
    6: [[4,0]]
}

char_codes = {
    1: {0: '.', 2: ',', 5: 'i', 8: ':', 10: ';', 12: '|', 13: '!'},
    2: {0: "'", 1: 'l'},
    3: {0: ']', 1: '[', 2: 'I', 3: 't'},
    4: {0: ')', 1: '}', 2: '*', 4: '<', 6: 'k', 9: '>', 10: '(', 11: '"', 12: '{', 15: 'f'},
    5: {768: '+', 3713: '6', 1026: 'c', 1027: 'r', 2693: '$', 0: '_', 7: '=', 136: 'J', 1474: 'e', 14: '/', 
        656: '3', 1681: '8', 1171: '0', 512: '-', 3991: '#', 657: '9', 154: 'S', 1179: 'G', 312: 'T', 1219: 'n', 
        1075: 'P', 1187: 'b', 1169: 'O', 1193: 'U', 1159: 'p', 1736: 'd', 45: 'V', 1201: 'D', 1203: 'B', 
        837: 'x', 824: '7', 1081: 'F', 187: '5', 3392: '&', 1217: 'u', 450: 'a', 1475: 'm', 1732: 'q', 1221: 'y',
        1222: 'g', 1121: 'L', 1480: '4', 258: 's', 3817: 'N', 2368: '1', 1233: 'Q', 1473: 'w', 1235: 'A', 
        2144: '\\', 592: '2', 1251: 'h', 2049: '^', 1154: 'o', 1041: 'C', 3816: 'X', 1769: 'K', 1259: 'H', 
        1517: 'W', 110: '%', 2344: 'Y', 839: 'z', 1267: 'R', 3305: 'M', 1157: 'v', 1145: 'E', 122: 'Z', 
        200: 'j', 784: '?'},
    6: {0: '~', 1: '@'}
}

def calc_char_code (subimg, flags):
    '''This is constructing a binary number'''
    return_val = 0
    for flag in flags:
        return_val *= 2

        # bbox gives cords for origin, flag gives offset
        x = flag[0]
        y = flag[1]
        px_val = subimg[y, x]

        if px_val > 100:
            return_val += 1
    
    return return_val

def read_bboxes (binary_img, bboxes):
    '''
    Reads the image in the order of the bboxes
    Unknown/ Unrecognized characters are replaced with ? marks 
    '''
    return_string = ""

    for bbox in bboxes: 
        # Width = key
        key = bbox[1] - bbox[0]
        img_slice = binary_img[bbox[2]:bbox[3], bbox[0]:bbox[1]]
        char_code = calc_char_code(img_slice, flags_dict[key])

        if char_code in char_codes[key].keys():
            return_string += char_codes[key][char_code]
        else:
            return_string += '?'
    
    return return_string





'''
            Character Segmentation
'''
def extract_char_bboxes (text_img):
    '''
    Extracts the bounding box of each character,
    The return array is 3D
        first index > line (for newlines)
        second index > character on line
        third index > bbox cords
    '''
    line_bottoms = get_baselines(text_img)

    char_bboxes = []
    for baseline in line_bottoms:
        char_bboxes += [extract_bboxes_in_line(text_img, baseline)]
    
    return char_bboxes

def get_baselines (text_img):
    search_width = 50
    start_x = first_col_with_white(text_img)
    end_x = start_x + search_width

    lines_y = []
    white_in_strip = False
    prev_white_in_strip = False
    prev_slice = []
    for y_val, px_slice in enumerate(text_img[:, start_x:end_x]):
        if np.sum(px_slice) > 0:
            white_in_strip = True
        else:
            white_in_strip = False

        # Hit bottom of a line
        if not white_in_strip and prev_white_in_strip:
            # If a line's bottom is really flat, its bbox wont be
            # alligned. This is because pertruding characters (j, ,, g)
            # push it down one further. This percentage check corrects for it

            # This algorithm would fail if a line had many g, y, j, etc chars
            percent_white = np.sum(prev_slice) / 255 / search_width
            if percent_white > 0.1:
                lines_y += [y_val + 1]
            else:
                lines_y += [y_val]
        
        prev_white_in_strip = white_in_strip
        prev_slice = px_slice
    
    return lines_y

def first_col_with_white (text_img):
    for col_ind in range(len(text_img[0])):
        col = text_img[:, col_ind]
        if np.sum(col) != 0:
            return col_ind

    return len(text_img[0]) - 1

def extract_bboxes_in_line (text_img, line_y):
    # 8 = line_height, known because the font is known
    above_y = line_y - 8

    line_bboxes = []
    white_in_strip = False
    prev_white_in_strip = False
    left_x = 0
    for x_val in range(len(text_img[0])):
        px_strip = text_img[above_y:line_y, x_val]
        if np.sum(px_strip) > 0:
            white_in_strip = True
        else:
            white_in_strip = False

        # Pretty much the same logic as get_baselines
        if not white_in_strip and prev_white_in_strip:
            # left right top bottom <=> small big small big
            line_bboxes += [[left_x, x_val, above_y, line_y]]
        elif white_in_strip and not prev_white_in_strip:
            left_x = x_val
        
        prev_white_in_strip = white_in_strip

    return line_bboxes


