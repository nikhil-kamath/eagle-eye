import cv2
import numpy as np
import imutils

class BoundingBoxGenerator: 
    '''Class to give bounding box given an image'''
    def __init__(self, image_array=None, width=None):
        self.img_array = image_array
        self.w = width
        self.bounding_box = self.estimate()
    
    def estimate(self):
        # converts frame to grayscale
        gray_frame = cv2.cvtColor(self.img_array, cv2.COLOR_BGR2GRAY)
        # blurs frame
        blur_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

        # running edge detection
        edges = cv2.Canny(blur_frame, 35, 125)

        # getting largest contours from edges detected
        # assuming the largest contours result from the paper and the wall
        # cv2.RETR_LIST finds largest contours and organizes them in hierarchy
        # cv2.CHAIN_APPROX_SIMPLE just returns endpoints needed to construct the contours
        contours = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # final = cv2.drawContours(self.img_array, contours, contourIdx=-1, color=(255,0,0), thickness=2)
        final_contours = imutils.grab_contours(contours)
        final_box = max(final_contours, key=cv2.contourArea)

        # returns bounding box in form ((x, y), (w, h), something_lmao) 
        bounding_box = cv2.minAreaRect(final_box)

        return bounding_box
    
     
