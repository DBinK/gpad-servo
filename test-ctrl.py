
from threading import Thread
from time import sleep
import cv2
import keyboard
import cam

url = 3
vcap = cv2.VideoCapture(url)

x, y = 100, 100

# 定义按键监听函数
def key_listener():
    def release(event):
        global track
        print(event.name)
        if event.event_type == keyboard.KEY_UP:
            sleep(0.5)   # 消除抖动
            if event.name == 'q':
                print("q is pressed")
            elif event.name == 'w':
                print("w is pressed")
            elif event.name == 'e':
                print("e is pressed")
            elif event.name == 't':
                print("t is pressed")
                track = 1
    
    keyboard.on_release(release)  # 注册按键监听器
    keyboard.wait()  # 保持监听状态

track = 0

if __name__ == '__main__':
    # 创建一个线程来监听控制台按键输入
    #key_thread = Thread(target=key_listener)
    #key_thread.start()

    while True:
        # 读取每一帧图像
        ret, frame = vcap.read()

        red_point,green_point = cam.find_point(frame)

        if red_point[0] != 0:
            frame = cam.draw_point(frame, red_point)

        r_x, r_y = red_point[0], red_point[1]

        dx = r_x - x
        dy = r_y - y

        x = int(x + dx*0.2)
        y = int(y + dy*0.2)

        track_point = [x, y, 30, 30]

        frame = cam.draw_point(frame, track_point)

        # 显示图像
        cv2.imshow('VIDEO', frame)

        # 按键盘上的任意键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        sleep(0.1)

# 释放资源
vcap.release()
cv2.destroyAllWindows()