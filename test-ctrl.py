
from time import sleep
import cv2
import cam

url = 3
vcap = cv2.VideoCapture(url)

x, y = 100, 100
track = False

if __name__ == '__main__':

    while True:
        # 读取每一帧图像
        ret, frame = vcap.read()

        red_point,green_point = cam.find_point(frame)

        if red_point[0] != 0:
            frame = cam.draw_point(frame, red_point)
        
        if track:
            # 获取红点坐标
            r_x, r_y = red_point[0], red_point[1]

            # 计算红点坐标和跟踪点的差值
            dx = r_x - x
            dy = r_y - y

            x = int(x + dx*0.2)
            y = int(y + dy*0.2)

            track_point = [x, y, 30, 30]

            frame = cam.draw_point(frame, track_point)

        # 显示图像
        cv2.imshow('VIDEO', frame)

        # 按键盘上的任意键退出
        
        if cv2.waitKey(1) & 0xFF == ord('t'):
            track = not track
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        sleep(0.02)

# 释放资源
vcap.release()
cv2.destroyAllWindows()