from bounding_box import BoundingBoxGenerator
import cv2
import math
from resizer import ResizeWithAspectRatio

'''returns 4 tuples corresponding to corners of the points'''
def get_points(bounding_box):
    return (int(bounding_box[0][0]), int(bounding_box[0][1])), (int(bounding_box[1][0]), int(bounding_box[1][1])), (int(bounding_box[2][0]), int(bounding_box[2][1])), (int(bounding_box[3][0]), int(bounding_box[3][1]))

'''returns the calibrated focal length inputted a picture with a starting distance'''
def calibrate(image, initial_distance: float, initial_width: float) -> float:
    estimator = BoundingBoxGenerator(image_array=image, width=initial_width)
    box_dims = estimator.estimate()
    bounding_box = cv2.boxPoints(box_dims)

    p1, p2, p3, p4 = get_points(bounding_box)
    box_width = get_width(p1, p2, p3, p4)

    focal_length = (box_width * initial_distance) / initial_width

    return focal_length

def get_width(p1, p2, p3, p4):
    d1 = math.dist(p1, p2)
    d2 = math.dist(p1, p3)
    d3 = math.dist(p1, p4)
    return int(min([d1, d2, d3]))

def video_calibrate(filename: str, distance: float, width: float) -> float:
    cam = cv2.VideoCapture(filename)
    focal_lengths = []

    while True:
        ret, image = cam.read()
        if not ret:
            return sum(focal_lengths)/len(focal_lengths)

        image = ResizeWithAspectRatio(image, 720, 1080)
        focal_length = calibrate(image, distance, width)
        focal_lengths.append(focal_length)

