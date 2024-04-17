from time import sleep
import cv2
import cam

url = 0
vcap = cv2.VideoCapture(url)

x, y = 100, 100
track = True

kp = 0.2  # 比例增益
ki = 0.05  # 积分增益
kd = 0.05  # 微分增益

integral_error_x = 0  # 积分误差（X轴）
integral_error_y = 0  # 积分误差（Y轴）
prev_error_x = 0  # 上一帧误差（X轴）
prev_error_y = 0  # 上一帧误差（Y轴）

if __name__ == '__main__':
    while True:
        ret, frame = vcap.read()

        if url == 0:
            frame = cv2.flip(frame, 1)

        red_point, green_point = cam.find_point(frame)

        if red_point[0] != 0:
            frame = cam.draw_point(frame, red_point, color = 'track')

        if track:
            r_x, r_y = red_point[4], red_point[5]

            # 计算当前误差
            error_x = r_x - x
            error_y = r_y - y

            # 积分误差更新
            integral_error_x += error_x
            integral_error_y += error_y

            # 微分误差计算
            diff_error_x = error_x - prev_error_x
            diff_error_y = error_y - prev_error_y

            # PID控制输出
            u_x = kp * error_x + ki * integral_error_x + kd * diff_error_x
            u_y = kp * error_y + ki * integral_error_y + kd * diff_error_y

            # 更新跟踪点位置（限幅可选，避免剧烈震荡）
            x = int(x + u_x)
            y = int(y + u_y)

            track_point = [red_point[0], red_point[1], 30, 30, x, y]
            frame = cam.draw_point(frame, track_point)

            # 保存当前误差作为下一次微分误差计算的参考
            prev_error_x = error_x
            prev_error_y = error_y

        cv2.imshow('VIDEO', frame)

        if cv2.waitKey(1) & 0xFF == ord('t'):
            track = not track
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        sleep(0.0333333)

vcap.release()
cv2.destroyAllWindows()