import time 
import servo_driver

servo = servo_driver.ServoController()

x, y = 100, 100
track = True

kp = 0.2  # 比例增益
ki = 0.05  # 积分增益
kd = 0.05  # 微分增益

integral_error_x = 0  # 积分误差（X轴）
integral_error_y = 0  # 积分误差（Y轴）
prev_error_x = 0  # 上一帧误差（X轴）
prev_error_y = 0  # 上一帧误差（Y轴）


angle_x, angle_y = 90 ,90

limit = [60, 120]

def pid_ctrl(red_point, track_point):
    global x, y, track, angle_x, angle_y, prev_error_x, prev_error_y, ix, iy, track_done
    

    dx = x - red_point[4]
    dy = y - red_point[5]

    print(f"dx: {dx}, dy: {dy}")
    print(f"{angle_x}, {angle_y}")
    print(f"{x}, {y} \n")

    if abs(dx) > 5 or abs(dy) > 5:
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

        print("完成追踪")

        if track_point == 4 and track_done == 1:
            track_point = 1
            track_done = 0

        if track_point < 4 and track_point != 0 and track_done == 1:
            track_point = track_point + 1
        

        """ if track_point == 1 and track_done == 1:
            track_swtich = 0 """