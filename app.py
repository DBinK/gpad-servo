import keyboard
import time

from threading import Thread

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
    key_thread = Thread(target=key_listener)
    key_thread.start()