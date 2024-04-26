
import cv2
import cam
import scrcpy
from adbutils import adb

adb.connect("192.168.50.4:38679")

adb_device = adb.device_list()

client = scrcpy.Client(device=adb_device[0], bitrate=1000000, max_fps=60, max_width=1080, connection_timeout=3000)

# You can also pass an ADBClient instance to it
""" adb.connect("127.0.0.1:5555")
client = scrcpy.Client(device=adb.device_list()[0]) """
def on_frame(frame):
    # If you set non-blocking (default) in constructor, the frame event receiver 
    # may receive None to avoid blocking event.
    if frame is not None:

        processed_frame = frame.copy()

        contours = cam.preprocess_image(processed_frame)

        if contours is not None:
            vertices = cam.find_max_perimeter_contour(contours, 999999999, 100*4) # 最大,最小允许周长(mm)

        if vertices is not None:
            #print(f"四个顶点坐标:\n {vertices}")

            roi_frame = cam.roi_cut(processed_frame, vertices)
            red_point,green_point = cam.find_point(roi_frame)

            if red_point[0] != 0:
                processed_frame = cam.draw_point(processed_frame,red_point)
            else:
                red_point = [-1,-1]
                
            if green_point[0] != 0:
                processed_frame = cam.draw_point(processed_frame,green_point)
            else:
                green_point = [-1,-1]    

            processed_frame, new_vertices = cam.draw_contour_and_vertices(processed_frame, vertices, (500/600)) # 外框与内框宽度之比 
        # frame is an bgr numpy ndarray (cv2' default format)
        cv2.namedWindow('viz', cv2.WINDOW_NORMAL)
        cv2.imshow("viz", processed_frame)
    cv2.waitKey(1)

client.add_listener(scrcpy.EVENT_FRAME, on_frame)

client.start()
