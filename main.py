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

blur = 3
def get_display_image(image, focal_length):
    estimator = BoundingBoxGenerator(image_array=np.asarray(image), width=8.5)
    box_dims = estimator.estimate()
    bounding_box = cv2.boxPoints(box_dims)

    p1, p2, p3, p4 = cal.get_points(bounding_box)

    image = cv2.line(image, p2, p3, (0, 255, 0), 1) #top 
    image = cv2.line(image, p1, p4, (0, 255, 0), 1) #bottom
    image = cv2.line(image, p2, p1, (0, 255, 0), 1) #left
    image = cv2.line(image, p3, p4, (0, 255, 0), 1) #rightq


    distance = (8.5 * focal_length) / gw(p1, p2, p3, p4) # box_dims[1][0]

    cv2.putText(image, '{} inches'.format(str(distance)), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, 2)
    i = 1
    for point in (p1, p2, p3, p4):
        cv2.putText(image, str(i), point, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        i+=1

    return image, bounding_box

def start_loop(cam: cv2.VideoCapture, focal_length: float, filepath: string):
    printed = False
    while True:
        ret, image = cam.read() # read the image and resize it to the correct dimensions
        if not ret:
            cam = cv2.VideoCapture(filepath)
            continue

        image = ResizeWithAspectRatio(image, width=720, height=1280)

        if not printed:
            print(image.shape)
            printed = True
        
        image_with_box, bounding_box = get_display_image(image.copy(), focal_length)
        image = image_with_box # comment out to remove distance and bounding box display

        blurred_image = cv2.GaussianBlur(image, (blur, blur), cv2.BORDER_DEFAULT) # take a copy of the image and blur it to the desired level

        p1 = (int(bounding_box[1][0]), int(bounding_box[1][1])) # get the top left and bottom right coordinates of the bounding box
        p4 = (int(bounding_box[3][0]), int(bounding_box[3][1]))
        mask = np.zeros(image.shape[:2], dtype="uint8") # create a mask with a rectangle using these coordinates
        cv2.rectangle(mask, p1, p4, 255, -1)


        final_image = image.copy() # put the blurred image on top using the rectangular mask
        final_image[np.where(mask == 255)] = blurred_image[np.where(mask == 255)]
        cv2.imshow("masked image", final_image) # display on screen
        q = cv2.waitKey(20)
        if q == 113:
            break
    
        
if __name__ == '__main__':
    filepath = './assets/5ft.MOV'
    cam = cv2.VideoCapture(filepath)
    initial_distance = 60
    initial_width = 8.5
    focal_length = 1129.4117647058824
    calibration_image = ResizeWithAspectRatio(cam.read()[1], width=720, height=1080)
    focal_length = cal.calibrate(calibration_image, initial_distance, initial_width) # calibrate the focal length using the first frame


    m = threading.Thread(target=start_loop, args=(cam, focal_length, filepath)) # creating a thread to run the blur display part
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
