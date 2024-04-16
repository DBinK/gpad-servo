from threading import Thread
import time
import keyboard
import servo_driver

servo = servo_driver.ServoController()
angle = 90

# 定义按键监听函数
def key_listener():
    def release(event):
        global angle
        print(event.name)
        if event.event_type == keyboard.KEY_UP:
            # time.sleep(0.5)   # 消除抖动
            if event.name == 'q':
                print("q is pressed")
            elif event.name == 'w':
                print("w is pressed")

            elif event.name == 'a':
                angle += 1
                servo.rotate_angle(0, angle)
            elif event.name == 'd':
                angle -= 1
                servo.rotate_angle(0, angle)
    
    keyboard.on_press(release)  # 注册按键监听器
    keyboard.wait()  # 保持监听状态


if __name__ == '__main__':
    
    # 创建一个线程来监听控制台按键输入
    key_thread = Thread(target=key_listener)
    key_thread.start()
