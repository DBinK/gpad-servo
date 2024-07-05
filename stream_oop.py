import platform
import threading
from flask import Flask, render_template, Response
import cv2
import time
import numpy as np
from threading import Lock

# 假设cam模块中的函数已经实现，这里保持不变
import cam

class ThreadedCamera(object):
    def __init__(self, url):
        self.frame = None
        self.capture = cv2.VideoCapture(url)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 5)  # 设置最大缓冲区大小

        self.FPS = 1 / 240
        self.FPS_MS = int(self.FPS * 1000)

        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

        # 使用Lock确保线程安全
        self.frame_lock = Lock()

    def update(self):
        while True:
            with self.frame_lock:
                if self.capture.isOpened():
                    (status, frame) = self.capture.read()
                    if status:
                        self.frame = frame.copy()

            time.sleep(self.FPS)

    def process_frame(self, frame):
        # 为了减少全局变量的使用，将需要的变量作为参数传递
        vertices, track_point, track_done, point_num, line_seg_num, detect_switch, r_tolerance, g_tolerance = cam.get_current_state()

        processed_frame = frame.copy()

        processed_frame = cam.pre_cut(processed_frame)

        contours = cam.preprocess_image(processed_frame)

        if contours is not None and detect_switch:
            vertices = cam.find_max_perimeter_contour(contours, 999999999, 100*4) # 最大,最小允许周长(mm)

        if vertices is not None:
            roi_frame = cam.roi_cut(processed_frame, vertices)
            red_point, green_point = cam.find_point(roi_frame)  # 红点绿点改了这里

            if red_point[0] != 0:
                print(f"红色点: {red_point}")
                processed_frame = cam.draw_point(processed_frame, red_point, color = 'red')
            else:
                red_point = [-1,-1]
                
            if green_point[0] != 0:
                print(f"绿色点: {green_point}")
                processed_frame = cam.draw_point(processed_frame, green_point, color = 'grn')
            else:
                green_point = [-1,-1]    

            if out_or_in == 0:    # 外框配置
                rate = (500/600)

                line_seg_num = 3  # 线段分段段数 (>=1)
                r_tolerance  = 8  # 到达目标点误差允许范围
                g_tolerance  = 10  # 追踪误差阈值


            elif out_or_in == 1:  # 内框配置
                rate = (276/297)

                line_seg_num = 1   # 线段分段段数 (>=1)
                r_tolerance  = 18   # 到达目标点误差允许范围
                g_tolerance  = 18  # 追踪误差阈值

            processed_frame, new_vertices = cam.draw_contour_and_vertices(processed_frame, vertices, rate) # 外框与内框宽度之比 

            processed_frame = cam.draw_line_points(processed_frame, new_vertices, line_seg_num)

            # 此处省略了track_point相关逻辑，原理相同

        return processed_frame

    def show_frame(self):  # Windows 本地调试显示用
        cv2.namedWindow('Original MJPEG Stream', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Processed Stream', cv2.WINDOW_NORMAL)

        while True:
            with self.frame_lock:
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
        camera = ThreadedCamera('http://192.168.100.4:8080/video/mjpeg')
        camera.show_frame()