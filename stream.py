from flask import Flask, render_template, Response
import cv2
import time
import keyboard
from threading import Thread

from cam8 import draw_contour_and_vertices, find_max_perimeter_contour, preprocess_image


class ThreadedCamera(object):
    def __init__(self, url):
        self.frame = None
        self.capture = cv2.VideoCapture(url)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # 设置最大缓冲区大小

        # 设定帧率
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

    def process_frame_outside(self, frame):
        # 创建一个副本来存储处理后的帧
        processed_frame = frame.copy()

        # 在这里添加OpenCV处理代码
        contours = preprocess_image(processed_frame)
        if contours is not None:
            vertices = find_max_perimeter_contour(contours, 999999999, 400*4) # 最大,最小允许周长(mm)

        if vertices is not None:
            print(f"四个顶点坐标:\n {vertices}")
            processed_frame = draw_contour_and_vertices(processed_frame, vertices, (500/600)) # 外框与内框宽度之比 

        return processed_frame
    
    def process_frame_inside(self, frame):
        # 创建一个副本来存储处理后的帧
        processed_frame = frame.copy()

        # 在这里添加OpenCV处理代码
        contours = preprocess_image(processed_frame)
        if contours is not None:
            vertices = find_max_perimeter_contour(contours, 20000*4, 30*4) # 最大,最小允许周长(mm)
            print(f"四个顶点坐标:\n {vertices}")

        if vertices is not None:
            processed_frame = draw_contour_and_vertices(processed_frame, vertices, (276/297)) # 外框与内框宽度之比(mm) 靶纸是 (276/297)
        
        return processed_frame

    def show_frame(self):  # 本地调试显示用
        cv2.namedWindow('Original MJPEG Stream', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Original MJPEG Stream', 800, 600)
        cv2.namedWindow('Processed Stream', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Processed Stream', 800, 600)

        cv2.imshow('Original MJPEG Stream', self.frame)
        processed_frame = self.process_frame_outside(self.frame)  #!记得改这里
        if processed_frame is not None:
            cv2.imshow('Processed Stream', processed_frame)
        cv2.waitKey(self.FPS_MS)

def generate_frames():        
    # 320x240 640x480 960x720 1280x720 1920x1080
    #url = 'http://192.168.100.44:4747/video?960x720'
    url = 'http://192.168.100.44:4747/video?640x480'
    stream = ThreadedCamera(url)

    while True:
        frame = stream.frame
        if frame is not None:
            try:
                processed_frame = stream.process_frame_outside(frame)
                # 将处理后的帧编码为JPEG格式
                _, jpeg_buffer = cv2.imencode('.jpg', processed_frame)

                # 拼接MJPEG帧并返回
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + jpeg_buffer.tobytes() + b'\r\n')
            except Exception as e:
                print(f"Error processing frame: {e}")
                # 可以选择跳过该帧，继续处理下一帧，或者返回一个默认图像（如全黑图像）
                continue

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 定义按键监听函数
def key_listener():
    def release(event):
        print(event.name)
        if event.event_type == keyboard.KEY_UP:
            time.sleep(0.5)   # 消除抖动
            if event.name == 'q':
                print("q is pressed")
            elif event.name == 'w':
                print("w is pressed")
            elif event.name == 'e':
                print("e is pressed")
    
    keyboard.on_release(release)  # 注册按键监听器
    keyboard.wait()  # 保持监听状态

if __name__ == '__main__':
    # 创建一个线程来监听控制台按键输入
    #key_thread = Thread(target=key_listener)
    #key_thread.start()

    app.run(host='0.0.0.0', debug=True)

    
    # 320x240 640x480 960x720 1280x720 1920x1080
    """ stream_url = 'http://192.168.100.44:4747/video?960x720'
    threaded_camera = ThreadedCamera(stream_url)
    
    while True:
        try:
            threaded_camera.show_frame()
        except AttributeError:
            pass """


