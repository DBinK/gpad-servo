# 定义按键监听函数
import keyboard

import servo_driver

servo = servo_driver.ServoController()

def key_listener():
    def on_press(event):
        global servo_on, angle_y, angle_x, speed
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

            elif event.name == 'a':
                angle_x += speed
                servo.rotate_angle(0, angle_x) 
                print(f"{angle_x} <-")

            elif event.name == 'd':
                
                angle_x -= speed
                servo.rotate_angle(0, angle_x)
                print(f"{angle_x} ->")

            elif event.name == 'w':
                
                angle_y -= speed
                servo.rotate_angle(3, angle_y) 
                print(f"{angle_y} A")

            elif event.name == 's':
                
                angle_y += speed
                servo.rotate_angle(3, angle_y) 
                print(f"{angle_y} V")

            elif event.name == 'r':
                servo.reset()
                angle_y = 90
                angle_x = 90

                print("重置位置")

            elif event.name == 'q':
                servo.reset()
                angle_y = 90
                angle_x = 90
                print("退出程序")
    
    keyboard.on_press(on_press)  # 注册按键监听器
    keyboard.wait()  # 保持监听状态