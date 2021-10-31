from calibrator import video_calibrate
import json
import sys

filepath = input("enter filepath: ")
distance = float(input("enter distance video is taken from: "))
width = float(input("enter width of object in the video: "))

fl = video_calibrate(filepath, distance, width)
print("average focal length returned from calibration video:", fl)

with open("package_settings.json", 'w') as f:
    json.dump({"focal_length":fl}, f)

