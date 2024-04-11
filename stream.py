from flask import Flask, render_template, Response
import cv2
import time
from threading import Thread

from cam8 import draw_contour_and_vertices, find_contour_xy, find_max_perimeter_contour, preprocess_image


class ThreadedCamera(object):
    def __init__(self, url):
        self.frame = None
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
                    self.frame = frame.copy()
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

""" if __name__ == '__main__':
    # 320x240 640x480 960x720 1280x720 1920x1080
    stream_url = 'http://192.168.100.4:4747/video?640x480'
    threaded_camera = ThreadedCamera(stream_url)
    
    while True:
        try:
            threaded_camera.show_frame()
        except AttributeError:
            pass """

app = Flask(__name__)

def generate_frames():        
    # 320x240 640x480 960x720 1280x720 1920x1080
    url = 'http://192.168.100.4:4747/video?640x480'
    stream = ThreadedCamera(url)

    while True:
        frame = stream.frame
        if frame is not None:
            try:
                processed_frame = stream.process_frame(frame)
                # 将处理后的帧编码为JPEG格式
                ret, jpeg_buffer = cv2.imencode('.jpg', processed_frame)

                # 拼接MJPEG帧并返回
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + jpeg_buffer.tobytes() + b'\r\n')
            except Exception as e:
                print(f"Error processing frame: {e}")
                # 可以选择跳过该帧，继续处理下一帧，或者返回一个默认图像（如全黑图像）
                continue

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)