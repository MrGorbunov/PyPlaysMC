'''
OCR Calibrator Rewrite

This script works for the MC text OCR. It 'calibrates' or finds the optimal keys

There are a lot of constants that come from knowing exactly what image is the input.
'''

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

def display_all_heatmaps (bw_heatmaps, scale_factor):
    '''Displays an array of heatmaps side by side with 1 pixel of padding'''
    h, w = bw_heatmaps[0].shape
    heatmap_width = w

    # 1 px padding
    h += 2
    w = (w + 1) * len(bw_heatmaps) + 1

    end_img = np.zeros((h, w, 3), dtype='uint8')
    end_img[:, :] = (100, 20, 10)

    for ind, heatmap in enumerate(bw_heatmaps):
        subimg_x = ind * (heatmap_width + 1) + 1
        end_img[1:-1, subimg_x:subimg_x + heatmap_width] = colorize_heatmap(heatmap, True)[:, :]
    
    display_at_scale(end_img, scale_factor)


    


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

print(char_bboxes[0])


'''
           Seperating characters
'''
# character width =  key
bboxes_dict = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': []}
chars_dict = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': []}
# these match the image and also the order of the char_bboxes
chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890' \
        '!@#$%^&*()-_=+~[{}]:;"\'<>,.?/\\|'

for ind, bbox in enumerate(char_bboxes):
    key = str(bbox[1] - bbox[0])
    bboxes_dict[key] += [bbox]
    chars_dict[key] += [chars[ind]]



'''
           Heatmap generation
'''
def get_heatmap (img, bboxes):
    '''Requires all bboxes be the same size, throws error if not'''
    cur_box = bboxes[0]
    w = cur_box[1] - cur_box[0]
    h = cur_box[2] - cur_box[3]
    heatmap = np.zeros((h, w), dtype="uint8")

    for cur_box in bboxes:
        heatmap[:, :] += img[cur_box[3]:cur_box[2], cur_box[0]:cur_box[1]] // 255
    heatmap *= (255 // len(bboxes))

    return heatmap

def avg_heatmaps (heatmaps, biases):
    '''Computes a weighted average of heatmaps. 
        The two inputs are parallel arrays'''
    h, w = heatmaps[0].shape
    avged_heatmap = np.zeros((h, w), dtype="uint8")
    tot_bias = 0

    for ind in range(len(heatmaps)):
        bias = biases[ind]
        tot_bias += bias
        avged_heatmap[:, :] += heatmaps[ind][:, :] * bias
    
    avged_heatmap[:, :] *= 255 // tot_bias
    return avged_heatmap

def colorize_heatmap (img, hot_center=True):
    result = img.copy()

    if hot_center:
        # We want to stress the 50% region of the image
        # This transformation makes it so that the middle values are displayed hot
        for y in range(len(result)):
            for x in range(len(result[0])):
                # 0, 255 -> 0;  127 -> 255
                result[y, x] = 255 - (abs(127 - result[y, x]) * 2)

    result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
    result = cv2.applyColorMap(result, cv2.COLORMAP_HOT)
    return result



# This is not storing the values, is just for display
for width in range(1, 2):
    key = str(width)
    heatmap = get_heatmap(char_img, bboxes_dict[key])

    heatmap = colorize_heatmap(heatmap)
    display_at_scale(heatmap, 25, key)




'''
           Flag Picking
'''
# We select for flags that split the dataset into ~50%
# This means that at a minimum we need log2(bboxes) flags
# The following implements a recursive algorithm and so
# produces near optimal results
def get_best_flag ():
    '''
    Based on user input
    '''
    iter = 0

    while True:
        iter += 1
        if iter > 100:
            return

        try:
            x, y = input("flag: ")
            break
        except:
            pass
    
    return [x, y]


def bias_center (num):
    '''
    maps 127 -> 255, and 0, 254, 255 -> 0
    :param num: a number (0-255)
    :return: the shifted value
    '''
    if num == 255:
        return 0
    return 255 - abs(num - 127) * 2

def split_by_flag (img, bboxes, flag):
    '''Returns two lists, each containing bboxes after being sorted based on the flag'''
    yes_flag = []
    no_flag = []

    for bbox in bboxes:
        flag_x = bbox[0] + flag[0]
        flag_y = bbox[3] + flag[1]
        pix_val = img[flag_y, flag_x]

        if pix_val != 0:
            yes_flag += [bbox]
        else:
            no_flag += [bbox]
    
    ret_arr = []
    if len(yes_flag) > 0:
        ret_arr += [yes_flag]
    if len(no_flag) > 0:
        ret_arr += [no_flag]

    return ret_arr

def generate_flag_cords (img, bboxes):
    # Round 1
    flags = []
    dead_flags = []
    heatmaps = [get_heatmap(img, bboxes)]

    print("Starting flag selection for new width")
    print("dim:" + str(heatmaps[0].shape))
    display_at_scale(colorize_heatmap(heatmaps[0]), 16, "l")

    flags += [get_best_flag()]
    bbox_groups = split_by_flag(img, bboxes, flags[-1])


    # Rest of rounds are in a loop
    while len(bbox_groups) < len(bboxes):
        biases = []
        heatmaps = []

        # Generate heatmap for this iteration
        for group in bbox_groups:
            if len(group) <= 1:
                continue

            biases += [len(bbox)]
            heatmaps += [get_heatmap(img, group)]
        
        heatmaps += [avg_heatmaps(heatmaps, biases)]
        
        display_all_heatmaps(heatmaps, 16)
        flags += [get_best_flag()]

        # Get new groups for next round
        new_bbox_groups = []
        for group in bbox_groups:
            new_bbox_groups += split_by_flag(img, group, flags[-1])
        bbox_groups = new_bbox_groups




    # For debug, we also show the final round where everything is seperated
    heatmaps = []
    for group in bbox_groups:
        heatmaps += [get_heatmap(img, group)]
    display_all_heatmaps(heatmaps, 8)


    print("Len of groups and of total # bboxes")
    print(len(bbox_groups))
    print(len(bboxes))
    print(flags)
    return flags

def verify_flags (img, bboxes, flags):
    '''Verifies that the given flags provide unique classification'''
    identifiers = {}

    for bbox in bboxes:
        id = 0
        x = bbox[0]
        y = bbox[3]

        for flag in flags:
            x_off = flag[0]
            y_off = flag[1]
            id *= 2
            id += img[y+y_off, x+x_off]

        if id in identifiers.keys():
            print(identifiers.keys())
            print(id)
            return False
        else:
            identifiers[id] = True

    return True


flag_cords = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': []}

for key in flag_cords.keys():
    print("Starting key: " + str(key))

    flag_cords[key] = generate_flag_cords(char_img, bboxes_dict[key])

    display_flags_over_image(char_img, bboxes_dict[key], flag_cords[key])
    print(verify_flags(char_img, bboxes_dict[key], flag_cords[key]))




