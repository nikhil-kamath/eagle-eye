from bounding_box import BoundingBoxGenerator
from resizer import ResizeWithAspectRatio
from PIL import Image
import numpy as np
import cv2
import time
import imutils

blur = 1

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

    return img_arr, focal_length



if __name__ == '__main__':
    cam = cv2.VideoCapture('./assets/urmom3.MOV')
    focal_length = 1174.5882352941176
    initial_distance = 48
    printed = False
    while True:
        ret, image= cam.read()
        if not ret: 
            break

        image = ResizeWithAspectRatio(image, width=720, height=1280)

        img_arr = np.asarray(image)

        if not printed:
            print(img_arr.shape)
            printed = True
        
        img_arr, focal_length = get_display_image(image, img_arr, focal_length, initial_distance)

        cv2.imshow('ur mom', img_arr)
        k = cv2.waitKey(20)
        if k == 113:
            break
    
    print("focal length:", focal_length)
