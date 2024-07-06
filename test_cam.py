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

        self.FPS    = 1 / 240
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
            # 尝试执行的代码块
            vertices, scale_vertices, intersection = quad_detector.detect(img)
            img_drawed  = quad_detector.draw()

            red_point, green_point = point_detector.detect(img, quad_detector.vertices)
            img_drawed = point_detector.draw(img_drawed)        

        except Exception as e:
            print(f"发生错误: {e}")  
            img_drawed = img  

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

def generate_frames(camera):
    while True:
        with camera.frame_lock:
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
    camera = ThreadedCamera('http://192.168.50.4:8080/video/mjpeg')
    return Response(generate_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    if platform.system() == 'Linux':
        app.run(host='0.0.0.0', debug=True)
    else:
        # camera = ThreadedCamera('http://192.168.100.4:8080/video/mjpeg')
        camera = ThreadedCamera(0)
        camera.show_frame()