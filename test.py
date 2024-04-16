import keyboard
import servo_driver

servo = servo_driver.ServoController()

top_angle = 90
btn_angle = 90
speed = 0.3
on = 1

def on_key_press(event):
    global top_angle, btn_angle, speed, on

    if event.name == 'a':
        
        btn_angle += speed
        servo.rotate_angle(0, btn_angle) 
        print(f"{btn_angle} <-")

    elif event.name == 'd':
        
        btn_angle -= speed
        servo.rotate_angle(0, btn_angle)
        print(f"{btn_angle} ->")

    elif event.name == 'w':
        
        top_angle -= speed
        servo.rotate_angle(3, top_angle) 
        print(f"{top_angle} A")

    elif event.name == 's':
        
        top_angle += speed
        servo.rotate_angle(3, top_angle) 
        print(f"{top_angle} V")

    elif event.name == 'r':
        servo.reset()
        top_angle = 90
        btn_angle = 90

        print(f"重置位置")

    elif event.name == 'space':
        if on:
            servo.release()
            on = 0
            print(f"暂停控制")
        else:
            servo.restore()
            on = 1
            print(f"恢复控制")


keyboard.on_press(on_key_press)
keyboard.wait()