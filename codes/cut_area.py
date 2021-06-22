import numpy as np
import matplotlib.pyplot as plt
import cv2
import time
from pathlib import Path
import up_down
import datetime
from PIL import Image
from urllib.request import urlopen
import os

def mark_cut_area(block):

    ret = 0

    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    print(current_month)
    print(current_year)
    print(block)
    print(type(current_month))
    print(type(current_year))
    print(type(block))

    if(current_month == 1):
        previous_year = current_year - 1
        previous_month = 12

    else:
        previous_year = current_year
        previous_month = current_month - 1 

    current_recreated_image = up_down.download_images_for_checking_the_cut_area(current_year, current_month, block)
    previous_recreated_image = up_down.download_images_for_checking_the_cut_area(previous_year, previous_month, block)

    current_recreated_image_name = current_recreated_image["name"]
    previous_recreated_image_name = previous_recreated_image["name"]

    print(current_recreated_image_name)
    print(previous_recreated_image_name)

    if((previous_recreated_image_name == "recreated_image.png") and (current_recreated_image_name == "recreated_image.png")):

        current_recreated_image_url = current_recreated_image["url"]
        current_recreated_image_url = current_recreated_image_url.replace(" ", "+")  
        print(current_recreated_image_url)
        current_recreated_image_img = Image.open(urlopen(current_recreated_image_url)).convert('RGB')

        previous_recreated_image_url = previous_recreated_image["url"]
        previous_recreated_image_url = previous_recreated_image_url.replace(" ", "+") 
        print(previous_recreated_image_url) 
        previous_recreated_image_img = Image.open(urlopen(previous_recreated_image_url)).convert('RGB')

        current_recreated_image_img.save('var_current'+ '.png')
        previous_recreated_image_img.save('var_previous'+ '.png')

        img_after_cut = cv2.imread('var_current.png', cv2.IMREAD_COLOR)
        img_before_cut = cv2.imread('var_previous.png', cv2.IMREAD_COLOR)

        #os.remove('var_current'+ '.png')
        #os.remove('var_previous'+ '.png')

        # B G R
        light_brown = (30, 40, 50)
        dark_brown = (40, 60, 90)

        mask_before = cv2.inRange(img_before_cut, light_brown, dark_brown)
        mask_after = cv2.inRange(img_after_cut, light_brown, dark_brown)

        diff = cv2.absdiff(mask_before, mask_after)

        height = diff.shape[0]
        width = diff.shape[1]

        height = diff.shape[0]
        width = diff.shape[1]

        diff2 = np.zeros((height, width, 1), np.uint8)

        for i in range(0, height):
            for j in range(0, width):
                if((diff[i, j] == mask_before[i, j]) and (mask_before[i, j] == 255)):
                    diff2[i, j] = 0  
                else:
                    diff2[i, j] = diff[i,j]

        ret,thresh = cv2.threshold(diff2,25,255,cv2.THRESH_BINARY)

        # Find the contour of the figure 
        image, contours, hierarchy = cv2.findContours(
                                        image = thresh, 
                                        mode = cv2.RETR_TREE, 
                                        method = cv2.CHAIN_APPROX_SIMPLE)

        # Sort the contours 
        contours = sorted(contours, key = cv2.contourArea, reverse = True)
        # Draw the contour 
        img_copy = img_after_cut.copy()
        final = cv2.drawContours(img_copy, contours, contourIdx = -1, 
                                color = (0, 0, 200), thickness = 5)
        
        #cv2.imshow("original image", img_after_cut_with_clouds)
        #cv2.imshow("cut marked image", thresh)
        cv2.imshow("cut marked image", diff2)
        #cv2.imshow("cut marked image", final)
        cv2.imwrite('cut marked image.png', final) 
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        up_down.upload_cut_area_image(final, block)

        ret = 1

    return(ret)       