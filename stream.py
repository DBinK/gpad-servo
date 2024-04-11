import cv2
import time
from threading import Thread

from cam8 import draw_contour_and_vertices, find_contour_xy, find_max_perimeter_contour, preprocess_image


class ThreadedCamera(object):
    def __init__(self, url):
        self.capture = cv2.VideoCapture(url)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # 设置最大缓冲区大小

        # 设定帧率为30帧每秒
        self.FPS = 1 / 60
        self.FPS_MS = int(self.FPS * 1000)

        # 启动帧检索线程
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                (status, frame) = self.capture.read()
                if status:
                    self.frame = frame
            time.sleep(self.FPS)

    def process_frame(self, frame):
        # 在这里添加您的OpenCV处理代码
        # 例如，可以进行图像处理、对象检测、人脸识别等

        contours = preprocess_image(frame)
        max_perimeter, max_cnt = find_max_perimeter_contour(contours)

        if max_cnt is not None:
            vertices = find_contour_xy(max_cnt, max_perimeter)

        if vertices is not None:
            frame = draw_contour_and_vertices(frame, vertices)
            #frame = draw_max_cnt_rectangle(frame, vertices)

        processed_frame = frame
        
        #processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 示例：将帧转换为灰度图像
        return processed_frame

    def stream_as_mjpeg(self, processed_frame):
        # 启动一个http服务器，推送mjpeg流
        while True:
            processed_frame = self.process_frame(self.frame)
            if processed_frame is not None:
                ret, jpeg = cv2.imencode('.jpg', processed_frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    def show_frame(self):
        cv2.namedWindow('Original MJPEG Stream', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Original MJPEG Stream', 800, 600)
        cv2.namedWindow('Processed Stream', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Processed Stream', 800, 600)

        cv2.imshow('Original MJPEG Stream', self.frame)
        processed_frame = self.process_frame(self.frame)
        if processed_frame is not None:
            cv2.imshow('Processed Stream', processed_frame)
        cv2.waitKey(self.FPS_MS)

if __name__ == '__main__':
    # 320x240 640x480 960x720 1280x720 1920x1080
    stream_url = 'http://192.168.100.4:4747/video?640x480'
    threaded_camera = ThreadedCamera(stream_url)
    
    while True:
        try:
            threaded_camera.show_frame()
        except AttributeError:
            pass