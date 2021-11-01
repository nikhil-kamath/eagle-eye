from bounding_box import BoundingBoxGenerator
from resizer import ResizeWithAspectRatio
from PIL import Image
import numpy as np
import cv2
import time
import threading
from time import sleep
import calibrator as cal
from calibrator import get_width as gw
import string
from blur_to_power.blur_to_power import blur_to_power
import json
from typing import Dict

blur = 3
def get_display_image(image, focal_length, object_width):
    estimator = BoundingBoxGenerator(image_array=np.asarray(image))
    box_dims = estimator.estimate()
    bounding_box = cv2.boxPoints(box_dims)

    p1, p2, p3, p4 = cal.get_points(bounding_box)

    distance = (object_width * focal_length) / gw(p1, p2, p3, p4) # box_dims[1][0]

    if abs(distance - 60) < 5:
        color = (0, 255, 0)

        sugg_text = ":)"
    else:
        color = (0, 0, 255)
    
        if distance < 60:
            sugg_text = "go further"
        else:
            sugg_text = "go closer"

    image = cv2.line(image, p2, p3, color, 3) #top 
    image = cv2.line(image, p1, p4, color, 3) #bottom
    image = cv2.line(image, p2, p1, color, 3) #left
    image = cv2.line(image, p3, p4, color, 3) #rightq

    cv2.putText(image, '{} inches'.format(str(distance)), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, 2)
    cv2.putText(image, '{}'.format(str(sugg_text)), (60, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    i = 1
    for point in (p1, p2, p3, p4):
        cv2.putText(image, str(i), point, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        i+=1

    return image, bounding_box

def start_loop(cam: cv2.VideoCapture, focal_length: float, object_width: float, filepath: string):
    printed = False
    
    size = (720, 1280) 
    result = cv2.VideoWriter('tom_brady_demo.avi', cv2.VideoWriter_fourcc(*'MJPG'), 25, size)

    while True:
        ret, image = cam.read() # read the image and resize it to the correct dimensions
        if not ret:
            break
            # cam = cv2.VideoCapture(filepath)
            # continue

        image = ResizeWithAspectRatio(image, width=720, height=1280)

        if not printed:
            print(image.shape)
            printed = True
        
        image_with_box, bounding_box = get_display_image(image.copy(), focal_length, object_width)
        image = image_with_box # comment out to remove distance and bounding box display

        blurred_image = cv2.GaussianBlur(image, (blur, blur), cv2.BORDER_DEFAULT) # take a copy of the image and blur it to the desired level

        p1 = (int(bounding_box[1][0]), int(bounding_box[1][1])) # get the top left and bottom right coordinates of the bounding box
        p4 = (int(bounding_box[3][0]), int(bounding_box[3][1]))
        mask = np.zeros(image.shape[:2], dtype="uint8") # create a mask with a rectangle using these coordinates
        cv2.rectangle(mask, p1, p4, 255, -1)


        final_image = image.copy() # put the blurred image on top using the rectangular mask
        final_image[np.where(mask == 255)] = blurred_image[np.where(mask == 255)]
        result.write(final_image)
        cv2.imshow("masked image", final_image) # display on screen
        q = cv2.waitKey(20)
        if q == 113:
            break
    
        
if __name__ == '__main__':
    filepath = './assets/{}.MOV'.format(input("enter filepath: "))
    width = float(input("estimate object's width: "))
    cam = cv2.VideoCapture(filepath)
    focal_length: float
    data: Dict

    with open("package_settings.json") as f:
        data = json.loads(f.read())

        if "focal_length" not in data:
            print("calibration not found, running new calibration")
            filepath = input("enter filepath: ")
            distance = float(input("enter distance video is taken from: "))
            width = float(input("enter width of object in the video: "))
            fl = cal.video_calibrate(filepath, distance, width)

            data["focal_length"] = fl
        
        focal_length = data["focal_length"]

    with open("package_settings.json", 'w') as f:
        json.dump(data, f)        

    m = threading.Thread(target=start_loop, args=(cam, focal_length, width, filepath)) # creating a thread to run the blur display part
    m.daemon = True
    m.start()

    while True:  # loop to adjust the blur level using the cmd
        newblur = input()
        if newblur:
            if newblur == "out":
                break
            
            try:
                newblur = int(newblur)
            except ValueError:
                print("invalid blur value")
                continue

            blur = newblur*2 + 1
            print

    print("focal length:", focal_length)
    print('power: 20/', blur_to_power((blur-1)//2), sep="")