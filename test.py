import keyboard
import servo_driver

servo = servo_driver.ServoController()

top_angle = 90
btn_angle = 90

def on_key_press(event):
    global top_angle, btn_angle
    speed = 0.5

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


keyboard.on_press(on_key_press)
keyboard.wait()