import platform
import threading
from flask import Flask, render_template, Response
import cv2
import time
import numpy as np
import detector

quad_detector = detector.QuadDetector(20100, 100, 500/600)
point_detector = detector.PointDetector()

class ThreadedCamera(object):
    def __init__(self, url=0):
        self.frame   = None
        self.capture = cv2.VideoCapture(url)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 5)  # 设置最大缓冲区大小

        self.FPS    = 1 / 240  # 设置检测采样速率,单位为秒, 默认为240帧每秒
        self.FPS_MS = int(self.FPS * 1000)

        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                (status, frame) = self.capture.read()
                if status:
                    self.frame = frame.copy()

            time.sleep(self.FPS)

    def process_frame(self, frame):

        img = frame
    
        try:
            # 获取四边形的 顶点坐标, 中心点坐标
            vertices, scale_vertices, intersection = quad_detector.detect(img)
            img_drawed  = quad_detector.draw()

            # 获取 红点 和 绿点 的坐标
            red_point, green_point = point_detector.detect(img, quad_detector.vertices)
            img_drawed = point_detector.draw(img_drawed)        

        except Exception as e:
            print(f"未识别到矩形: {e}")  
            img_drawed = img 

        # 可以把控制代码放在这里, 此时控制频率和数据采样频率同步
        # 
        # 也可以另外再开一个线程, 只在需要时读取数据进行控制, 减小性能开销

        return img_drawed

    def show_frame(self):  # Windows 本地调试显示用
        cv2.namedWindow('Original MJPEG Stream', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Processed Stream', cv2.WINDOW_NORMAL)

        while True:

            frame = self.frame

            if frame is not None:
                try:
                    processed_frame = self.process_frame(frame)
                    if processed_frame is not None:
                        cv2.imshow('Processed Stream', processed_frame)
                except Exception as e:
                    print(f"Error processing frame: {e}")
                    continue

            cv2.imshow('Original MJPEG Stream', frame)
            key = cv2.waitKey(self.FPS_MS)
            if key == 27:  # ESC键退出
                break

        cv2.destroyAllWindows()


##############################################################################
# Flask 服务器相关代码

def generate_frames(camera):
    """
    生成帧的函数
    """
    while True:
        frame = camera.frame

        if frame is not None:
            try:
                processed_frame = camera.process_frame(frame)
                if processed_frame is not None:
                    _, jpeg_buffer = cv2.imencode('.jpg', processed_frame)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg_buffer.tobytes() + b'\r\n')
            except Exception as e:
                print(f"Error processing frame: {e}")
                continue

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    url = 'http://192.168.1.207:8080/video/mjpeg'  # 更改为数字0使用第0个硬件摄像头, 也可以使用视频文件地址或者视频流网址
    camera = ThreadedCamera(url)
    return Response(generate_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


##############################################################################
# 主函数
if __name__ == '__main__':

    if platform.system() == 'Linux': 
        # 启动 Flask 服务器
        app.run(host='0.0.0.0', debug=True)

    else:   # 更改为数字0使用第0个硬件摄像头, 也可以使用视频文件地址或者视频流网址
        url = 'http://192.168.1.207:8080/video/mjpeg'  
        camera = ThreadedCamera(url)
        camera.show_frame()