import platform

from flask import Flask, render_template, Response
import cv2
import time
import keyboard
from threading import Thread

import servo_driver
import cam
from cam import pre_cut, roi_cut, draw_point, find_point, draw_contour_and_vertices, find_max_perimeter_contour, preprocess_image

servo = servo_driver.ServoController()

angle_x, angle_y = 90 ,90
kd = 0.005

# 初始化键盘参数
servo_on = 1
ctrl_speed = 0.3

# 初始化追踪点, 中心点: 0 , 四个角点: 1, 2, 3, 4
track_point  = 0
track_done   = 0
track_swtich = 0

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
        global vertices, angle_x, angle_y, ctrl_speed, track_point, track_done, track_swtich
        processed_frame = frame.copy()

        processed_frame = pre_cut(processed_frame)

        # 在这里添加OpenCV处理代码
        contours = preprocess_image(processed_frame)
        if contours is not None:
            vertices = find_max_perimeter_contour(contours, 999999999, 100*4) # 最大,最小允许周长(mm)

        if vertices is not None:
            #print(f"四个顶点坐标:\n {vertices}")

            roi_frame = roi_cut(processed_frame, vertices)
            red_point,green_point = find_point(roi_frame)

            if red_point[0] != 0:
                processed_frame = draw_point(processed_frame,red_point)
            else:
                red_point = [-1,-1]
                
            if green_point[0] != 0:
                processed_frame = draw_point(processed_frame,green_point)
            else:
                green_point = [-1,-1]    

            processed_frame, new_vertices = draw_contour_and_vertices(processed_frame, vertices, (500/600)) # 外框与内框宽度之比 

            if track_point == 0:
                x ,y = cam.calculate_intersection(vertices)

            elif track_point == 1:
                x ,y = new_vertices[1] #第一个角点

            elif track_point == 2:
                x ,y = new_vertices[2] #第二个角点
            
            elif track_point == 3:
                x ,y = new_vertices[3] #第二个角点

            elif track_point == 4:
                x ,y = new_vertices[0] #第二个角点


            if x != 0 and red_point != [-1,-1] and track_swtich:
                try: # 启动 PD 控制算法
                    limit = [60, 120]

                    dx = x - red_point[4]
                    dy = y - red_point[5]

                    print(f"dx: {dx}, dy: {dy}")
                    print(f"{angle_x}, {angle_y}")
                    print(f"{x}, {y} \n")

                    if abs(dx) > 5 or abs(dy) > 5:
                        track_done = 0

                        angle_x = angle_x - (dx * kd)
                        angle_y = angle_y + (dy * kd) #这里取正负方向

                        if angle_x < limit[0]: 
                            angle_x = limit[0]
                            
                        if angle_y > limit[1]:
                            angle_y = limit[1]
                                        
                        servo.rotate_angle(0, angle_x)
                        servo.rotate_angle(3, angle_y)

                    else:
                        time.sleep(0.5) 

                        if track_point == 4 and track_done == 0:
                            track_point = 1

                        if track_point < 4 and track_point != 0:
                            track_point = track_point + 1
                            
                        track_done = 1

                        """ if track_point == 1 and track_done == 1:
                            track_swtich = 0 """

                except Exception as e:
                    print(f"无法启动舵机跟踪: {e}")

        return processed_frame
    
    def process_frame_inside(self, frame):
        # 创建一个副本来存储处理后的帧
        global vertices
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
        #processed_frame = self.process_frame_outside(self.frame)  #!记得改这里
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

# 定义按键监听函数
def key_listener():
    def on_press(event):
        global servo_on, angle_y, angle_x, ctrl_speed, track_point, track_swtich
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
                if track_swtich:
                    track_swtich = 0
                    print("暂停追踪")
                else:
                    track_swtich = 1
                    print("恢复追踪")

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
                track_swtich = 1
                print("追踪中点")
            
            elif event.name == '1':
                track_point = 1
                track_swtich = 1
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
            url = 'http://192.168.226.252:8080/video/mjpeg'
            stream = ThreadedCamera(url)

            while True:
                frame = stream.frame
                if frame is not None:
                    try:
                        #processed_frame = frame
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


