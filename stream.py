import platform

from flask import Flask, render_template, Response
import cv2
import time
import numpy as np
from threading import Thread

import cam

new_vertices = []
vertices = []
red_point, green_point = [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]

line_seg_num = 10   # 线段分段段数 (>=1)

r_tolerance = 8   # 到达目标点误差允许范围
g_tolerance = 10  # 追踪误差阈值


# 初始化追踪点, 中心点: 0 , 四个角点: 1, 2, 3, 4
track_point  = 0
track_done   = 0
red_track_switch = 0
grn_track_switch = 0
point_num    = 0
detect_switch = 1

out_or_in = 0  # 0: 外框, 1: 内框


class ThreadedCamera(object):
    def __init__(self, url):
        self.frame = None
        self.capture = cv2.VideoCapture(url)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 5)  # 设置最大缓冲区大小

        # 设定帧率
        self.FPS = 1 / 240
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
        
        global vertices, track_point, track_done
        global point_num, line_seg_num, detect_switch, r_tolerance, g_tolerance
        global new_vertices, red_point, green_point, red_track_switch, grn_track_switch

        processed_frame = frame.copy()

        processed_frame = cam.pre_cut(processed_frame)

        # 在这里添加OpenCV处理代码
        contours = cam.preprocess_image(processed_frame)

        if contours is not None and detect_switch:
            vertices = cam.find_max_perimeter_contour(contours, 999999999, 100*4) # 最大,最小允许周长(mm)

        if vertices is not None:
            #print(f"四个顶点坐标:\n {vertices}")
            if out_or_in == 0:
                roi_frame = cam.roi_cut(processed_frame, vertices)
                red_point, green_point = cam.find_point(roi_frame)  # 红点绿点改了这里

            elif out_or_in == 1:

                intersection = cam.calculate_intersection(vertices)  # 计算两个对角线的交点

                big_vertices = cam.shrink_rectangle(vertices, intersection[0], intersection[1], 2.0)

                roi_frame = cam.roi_cut(processed_frame, big_vertices)
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

            if track_point == 0:
                x ,y = cam.calculate_intersection(vertices)

            elif track_point == 1:
                points_list = cam.average_points(new_vertices[3], new_vertices[2], line_seg_num)
                x ,y = points_list[point_num] #第一个角点
                print(f"当前追踪1号点[{point_num}/{line_seg_num}]: {x}, {y}\n")

            elif track_point == 2:
                points_list = cam.average_points(new_vertices[2], new_vertices[1], line_seg_num)
                x ,y = points_list[point_num] 
                print(f"当前追踪2号点[{point_num}/{line_seg_num}]: {x}, {y}\n")

            elif track_point == 3:
                points_list = cam.average_points(new_vertices[1], new_vertices[0], line_seg_num)
                x ,y = points_list[point_num] 
                print(f"当前追踪3号点[{point_num}/{line_seg_num}]: {x}, {y}\n")

            elif track_point == 4:
                points_list = cam.average_points(new_vertices[0], new_vertices[3], line_seg_num)
                x ,y = points_list[point_num] 
                print(f"当前追踪4号点[{point_num}/{line_seg_num}]: {x}, {y}\n")

        return processed_frame

    def show_frame(self):  # Windows 本地调试显示用
        cv2.namedWindow('Original MJPEG Stream', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Processed Stream', cv2.WINDOW_NORMAL)
        cv2.imshow('Original MJPEG Stream', self.frame)

        processed_frame = self.process_frame(self.frame)  #!记得改这里
        if processed_frame is not None:
            cv2.imshow('Processed Stream', processed_frame)
        cv2.waitKey(self.FPS_MS)
        

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':

    if platform.system() == 'Linux':
        def generate_frames():     # 远程调试显示用
            url = 'http://192.168.50.4:8080/video/mjpeg'
            stream = ThreadedCamera(0)

            while True:
                frame = stream.frame
                if frame is not None:
                    try:
                        processed_frame = stream.process_frame(frame)
                        # 将处理后的帧编码为JPEG格式
                        _, jpeg_buffer = cv2.imencode('.jpg', processed_frame)

                        # 拼接MJPEG帧并返回
                        yield (b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\r\n' + jpeg_buffer.tobytes() + b'\r\n')
                    except Exception as e:
                        print(f"Error processing frame: {e}")
                        # 可以选择跳过该帧，继续处理下一帧，或者返回一个默认图像（如全黑图像）
                        continue

        app.run(host='0.0.0.0', debug=True)

    else:
        url = 'http://192.168.100.4:8080/video/mjpeg'

        threaded_camera = ThreadedCamera(url)

        while True:
            try:
                threaded_camera.show_frame()
            except AttributeError:
                pass