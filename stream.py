import cv2
import time
from threading import Thread



class ThreadedCamera(object):
    def __init__(self, url):
        self.capture = cv2.VideoCapture(url)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # 设置最大缓冲区大小

        # 设定帧率为30帧每秒
        self.FPS = 1 / 30
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
        processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 示例：将帧转换为灰度图像
        return processed_frame

    def show_frame(self):
        cv2.imshow('Original MJPEG Stream', self.frame)
        processed_frame = self.process_frame(self.frame)
        cv2.imshow('Processed Stream', processed_frame)
        cv2.waitKey(self.FPS_MS)

if __name__ == '__main__':
    stream_url = 'http://192.168.50.4:4747/video?640x480'
    threaded_camera = ThreadedCamera(stream_url)
    
    while True:
        try:
            threaded_camera.show_frame()
        except AttributeError:
            pass