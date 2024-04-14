import stream
import cam8
import cv2
import numpy as np
import time

import test_cam


# 320x240 640x480 960x720 1280x720 1920x1080
# url = 'http://192.168.100.4:4747/video?960x720'
url = 3 # 使用本地摄像头

cam = stream.ThreadedCamera(url)

while 1:
    try:
        cv2.namedWindow('Original MJPEG Stream', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Original MJPEG Stream', 800, 600)
        cv2.namedWindow('Processed Stream', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Processed Stream', 800, 600)

        cv2.imshow('Original MJPEG Stream', cam.frame)
        processed_frame = test_cam.find_red_circle(cam.frame)  #!记得改这里
        if processed_frame is not None:
            cv2.imshow('Processed Stream', processed_frame)

        cv2.waitKey(cam.FPS_MS)

    except AttributeError:
        pass