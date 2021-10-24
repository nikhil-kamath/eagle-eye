from bounding_box import BoundingBoxGenerator
from resizer import ResizeWithAspectRatio
from PIL import Image
import numpy as np
import cv2
import time
import imutils
import threading
from time import sleep


blur = 10

def get_display_image(image, img_arr, focal_length, initial_distance):
    estimator = BoundingBoxGenerator(image_array=img_arr, width=8.5)
    box_dims = estimator.estimate()
    bounding_box = cv2.boxPoints(box_dims)

    p1 = (int(bounding_box[0][0]), int(bounding_box[0][1]))
    p2 = (int(bounding_box[1][0]), int(bounding_box[1][1]))
    p3 = (int(bounding_box[2][0]), int(bounding_box[2][1]))
    p4 = (int(bounding_box[3][0]), int(bounding_box[3][1]))

    # top line 
    img_arr = cv2.line(image, p2, p3, (0, 255, 0), 10)
    # bottom line
    img_arr = cv2.line(image, p1, p4, (0, 255, 0), 10)
    # left line
    img_arr = cv2.line(image, p2, p1, (0, 255, 0), 10)
    # right line
    img_arr = cv2.line(image, p3, p4, (0, 255, 0), 10)

    width = abs(p2[0] - p3[0])
    # focal_length = 1163.2941176470588
    if focal_length == -1:
        focal_length = (width * initial_distance) / 8.5

    distance = (8.5 * focal_length) / box_dims[1][0] # box_dims[1][0]

    cv2.putText(img_arr, '{} inches'.format(str(distance)), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, 2)

    return img_arr, focal_length, bounding_box


def start_loop(cam: cv2.VideoCapture, focal_length: float, initial_distance: float):
    printed = False
    while True:
        ret, image = cam.read() # read the image and resize it to the correct dimensions
        if not ret:
            break

        image = ResizeWithAspectRatio(image, width=720, height=1280)
        img_arr = np.asarray(image)

        if not printed:
            print(img_arr.shape)
            printed = True
        
        img_arr, focal_length, bounding_box = get_display_image(image.copy(), img_arr, focal_length, initial_distance)
        image = img_arr # comment out to remove distance and bounding box display

        blurred_image = cv2.blur(image, (blur, blur)) # take a copy of the image and blur it to the desired level

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
    cam = cv2.VideoCapture('./assets/urmom3.MOV')
    focal_length = 1174.5882352941176 # set focal_length to -1 and adjust the initial_distance to calculate focal_length automatically from first frame
    initial_distance = 48
    printed = False

    m = threading.Thread(target=start_loop, args=(cam, focal_length, initial_distance)) # creating a thread to run the blur display part
    m.daemon = True
    m.start()

    while True:  # loop to adjust the blur level using the cmd
        newblur = input()
        if newblur:
            if newblur == "out":
                break

            newblur = int(newblur)
            if newblur % 2 != 0:
                newblur -= 1
            blur = newblur

    print("focal length:", focal_length)
