import cv2
import time
from threading import Thread

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

    def show_frame(self):
        cv2.imshow('MJPEG Stream', self.frame)
        cv2.waitKey(self.FPS_MS)

if __name__ == '__main__':
    stream_url = 'http://192.168.50.4:4747/video?640x480'
    threaded_camera = ThreadedCamera(stream_url)
    
    while True:
        try:
            threaded_camera.show_frame()
        except AttributeError:
            pass