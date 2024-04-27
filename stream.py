import platform

from flask import Flask, render_template, Response
import cv2
import time
import keyboard
from threading import Thread

import servo_driver
import cam

servo = servo_driver.ServoController()

angle_x, angle_y = 90 ,90
new_vertices = []
vertices = []
red_point, green_point = [0, 0], [0, 0]

kp = 0.02
ki = 0.0000001
kd = 0.02
line_seg_num = 4   # 线段分段段数 (>=1)
tolerance    = 8   # 到达目标点误差允许范围

# MG995
""" kp = 0.02
ki = 0.0000001
kd = 0.02
line_seg_num = 4   #线段分段段数 (>=1)
tolerance    = 5  #到达目标点误差允许范围 """

# PID 初始化
prev_error_x, prev_error_y = 0, 0
ix, iy = 0, 0
g_ix, g_iy, g_prev_error_x, g_prev_error_y = 0, 0, 0, 0

# 初始化键盘参数
servo_on = 1
ctrl_speed = 0.5

# 初始化追踪点, 中心点: 0 , 四个角点: 1, 2, 3, 4
track_point  = 0
track_done   = 0
track_switch = 0
point_num    = 0

detect_switch = 1

out_or_in = 0  # 0: 外框, 1: 内框

class ThreadedCamera(object):
    def __init__(self, url):
        self.frame = None
        self.capture = cv2.VideoCapture(url)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 5)  # 设置最大缓冲区大小

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
        global vertices, angle_x, angle_y, ctrl_speed, track_point, track_done, track_switch
        global ix, iy, prev_error_x, prev_error_y
        global point_num, line_seg_num, detect_switch, tolerance
        global new_vertices, red_point, green_point

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
                red_point, green_point = cam.find_point(processed_frame)  # 红点绿点改了这里

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

            if out_or_in == 0:
                rate = (500/600)

            elif out_or_in == 1:
                rate = (276/297)
                kp = 0.005
                ki = 0 #.0000001
                kd = 0.02
                line_seg_num = 4   # 线段分段段数 (>=1)
                tolerance    = 10   # 到达目标点误差允许范围

            processed_frame, new_vertices = cam.draw_contour_and_vertices(processed_frame, vertices, rate) # 外框与内框宽度之比 

            processed_frame = cam.draw_line_points(processed_frame, new_vertices, line_seg_num)

            if track_point == 0:
                x ,y = cam.calculate_intersection(vertices)

            elif track_point == 1:
                points_list = cam.average_points(new_vertices[3], new_vertices[2], line_seg_num)
                x ,y = points_list[point_num] #第一个角点
                print(f"当前追踪1号点: {x}, {y}\n")

            elif track_point == 2:
                points_list = cam.average_points(new_vertices[2], new_vertices[1], line_seg_num)
                x ,y = points_list[point_num] 
                print(f"当前追踪2号点: {x}, {y}\n")

            elif track_point == 3:
                points_list = cam.average_points(new_vertices[1], new_vertices[0], line_seg_num)
                x ,y = points_list[point_num] 
                print(f"当前追踪3号点: {x}, {y}\n")

            elif track_point == 4:
                points_list = cam.average_points(new_vertices[0], new_vertices[3], line_seg_num)
                x ,y = points_list[point_num] 
                print(f"当前追踪4号点: {x}, {y}\n")


            if x != 0 and red_point != [-1,-1] and track_switch:
                try: # 启动 PD 控制算法
                    limit = [60, 120]

                    dx = x - red_point[4]
                    dy = y - red_point[5]

                    print(f"dx: {dx}, dy: {dy}")
                    print(f"红点舵机角度: {angle_x}, {angle_y}")

                    if abs(dx) > tolerance or abs(dy) > tolerance:
                        track_done = 0

                        ix = ix + dx
                        iy = iy + dy

                        ddx = dx - prev_error_x
                        ddy = dy - prev_error_y

                        angle_x = angle_x - (kp*dx + ki*ix + kd * ddx)
                        angle_y = angle_y + (kp*dy + ki*iy + kd * ddy) #这里取正负方向

                        prev_error_x = dx
                        prev_error_y = dy

                        if angle_x < limit[0]: 
                            angle_x = limit[0]
                            
                        if angle_y > limit[1]:
                            angle_y = limit[1]
                                        
                        servo.rotate_angle(0, angle_x)
                        servo.rotate_angle(3, angle_y)

                    else:
                        time.sleep(0.5) 
                        
                        track_done = 1

                        if point_num < line_seg_num:
                            point_num += 1 
                            
                        else:
                            point_num = 0

                            if track_point == 4 and track_done == 1:
                                track_point = 1
                                track_done = 0

                            if track_point < 4 and track_point != 0 and track_done == 1:
                                track_point = track_point + 1 

                        print("完成追踪")                        

                except Exception as e:
                    print(f"无法启动舵机跟踪: {e}")

            if green_point != [-1,-1] and red_point != [-1,-1]:
                print(f"打开控制 grn_ctrl: {green_point}")
                grn_ctrl(red_point, green_point)

        return processed_frame



    def show_frame(self):  # 本地调试显示用
        cv2.namedWindow('Original MJPEG Stream', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Original MJPEG Stream', 800, 600)
        cv2.namedWindow('Processed Stream', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Processed Stream', 800, 600)

        cv2.imshow('Original MJPEG Stream', self.frame)

        
        processed_frame = self.process_frame_outside(self.frame)  #!记得改这里
        #processed_frame = self.process_frame_outside(self.frame)  #!记得改这里
        if processed_frame is not None:
            cv2.imshow('Processed Stream', processed_frame)
        cv2.waitKey(self.FPS_MS)
        


def grn_ctrl(red_point, green_point):

    global g_ix, g_iy, g_prev_error_x, g_prev_error_y

    kp = 0.005
    ki = 0 #.0000001
    kd = 0.02

    x = red_point[4]
    y = red_point[5]

    if green_point != [-1,-1] and track_switch:
        try: # 启动 PD 控制算法
            limit = [60, 120]

            dx = x - green_point[4]
            dy = y - green_point[5]

            print(f"绿点 dx: {dx}, dy: {dy}")
            print(f"绿点舵机角度: {angle_x}, {angle_y}")

            if abs(dx) > tolerance or abs(dy) > tolerance:

                ix = g_ix + dx
                iy = g_iy + dy

                ddx = dx - g_prev_error_x
                ddy = dy - g_prev_error_y

                angle_x = angle_x - (kp*dx + ki*ix + kd * ddx)
                angle_y = angle_y + (kp*dy + ki*iy + kd * ddy) #这里取正负方向

                g_prev_error_x = dx
                g_prev_error_y = dy

                if angle_x < limit[0]: 
                    angle_x = limit[0]
                    
                if angle_y > limit[1]:
                    angle_y = limit[1]
                                
                servo.rotate_angle(4, angle_x)
                servo.rotate_angle(7, angle_y)

            else:
                print("完成追踪")      
                time.sleep(0.5) 
        

        except Exception as e:
            print(f"无法启动舵机跟踪: {e}")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 定义按键监听函数
def key_listener():
    def on_press(event):
        global servo_on, angle_y, angle_x, ctrl_speed, track_point, track_switch, detect_switch, out_or_in
        print(event.name)
        if event.event_type == keyboard.KEY_DOWN:
            #time.sleep(0.5)   # 消除抖动
            if event.name == 'space':
                if servo_on:
                    servo.release()
                    servo_on = 0
                    print("暂停控制")
                else:
                    servo.restore()
                    servo_on = 1
                    print("恢复控制")

            if event.name == 'p':
                if track_switch:
                    track_switch = 0
                    detect_switch = 1
                    print("暂停追踪")
                else:
                    track_switch = 1
                    detect_switch = 0
                    print("恢复追踪")

            if event.name == 'o':
                if detect_switch:
                    detect_switch = 0
                    print("暂停图像检测")
                else:
                    detect_switch = 1
                    print("暂停图像检测")

            if event.name == 'i':
                if out_or_in == 1:
                    out_or_in = 0
                    print("切换到 外框")
                    time.sleep(1)
                else:
                    out_or_in = 1
                    print("切换到 内框")
                    time.sleep(1)
            

            elif event.name == 'a':
                angle_x += ctrl_speed
                servo.rotate_angle(0, angle_x) 
                print(f"{angle_x} <-")

            elif event.name == 'd':
                
                angle_x -= ctrl_speed
                servo.rotate_angle(0, angle_x)
                print(f"{angle_x} ->")

            elif event.name == 'w':
                
                angle_y -= ctrl_speed
                servo.rotate_angle(3, angle_y) 
                print(f"{angle_y} A")

            elif event.name == 's':
                
                angle_y += ctrl_speed
                servo.rotate_angle(3, angle_y) 
                print(f"{angle_y} V")

            elif event.name == 'r':
                servo.reset()
                angle_y = 90
                angle_x = 90

                print("重置位置")

            elif event.name == '0':
                track_point = 0
                track_switch = 1
                detect_switch = 0
                print("追踪中点")
            
            elif event.name == '1':
                track_point = 1
                track_switch = 1
                print("追踪1号点")
            
            elif event.name == '2':
                track_point = 2
                print("追踪2号点")

            elif event.name == '3':
                track_point = 3
                print("追踪3号点")

            elif event.name == '4':
                track_point = 4
                print("追踪4号点")

    
    keyboard.on_press(on_press)  # 注册按键监听器
    keyboard.wait()  # 保持监听状态


if __name__ == '__main__':
    # 创建一个线程来监听控制台按键输入
    key_thread = Thread(target=key_listener)
    key_thread.start()

    servo.reset()

    if platform.system() == 'Linux':
        def generate_frames():     # 远程调试显示用
            # 320x240 640x480 960x720 1280x720 1920x1080
            #url = 'http://192.168.100.44:4747/video?960x720'
            #url = 'rtsp://192.168.100.4:8080/video/h264'
            url = 'http://192.168.31.99:8080/video/mjpeg'
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

        app.run(host='0.0.0.0', debug=True)

    else:
        # 320x240 640x480 960x720 1280x720 1920x1080
        #url = 'http://192.168.100.4:4747/video?960x720'
        # url = 3 # 使用本地摄像头
        url = 'http://192.168.100.4:8080/video/mjpeg'
        #url = 'rtsp://192.168.100.4:8080/video/h264'

        threaded_camera = ThreadedCamera(url)

        while True:
            try:
                threaded_camera.show_frame()
            except AttributeError:
                pass


