import cv2
import datetime
import os
import threading
import numpy as np

def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)

blur = 1

def start_loop():
    vid = cv2.VideoCapture('Resources\demo.mp4')
    while True:
        ret, frame = vid.read()
        if not ret:
            vid = cv2.VideoCapture('Resources\demo.mp4')
            continue

        frame = ResizeWithAspectRatio(frame, height=1280)
        cv2.imshow('blurred', cv2.blur(frame, (blur, blur)))
        k = cv2.waitKey(20)
        if k == 113:
            break
    vid.release()



m = threading.Thread(target=start_loop)
m.daemon = True
m.start()

while True:
    newblur = input()
    if newblur:
        if newblur == "out":
            break

        newblur = int(newblur)
        if newblur % 2 != 0:
            newblur -= 1
        blur = newblur

cv2.destroyAllWindows()
