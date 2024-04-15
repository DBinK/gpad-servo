
from time import sleep
import cv2
import cam

url = 3
vcap = cv2.VideoCapture(url)

x, y = 100, 100

if __name__ == '__main__':

    while True:
        # 读取每一帧图像
        ret, frame = vcap.read()

        red_point,green_point = cam.find_point(frame)

        if red_point[0] != 0:
            frame = cam.draw_point(frame, red_point)
        
        # 获取红点坐标
        r_x, r_y = red_point[0], red_point[1]

        # 计算红点坐标和跟踪点的差值
        dx = r_x - x
        dy = r_y - y

        # 计算新的跟踪点坐标(PD算法)
        new_x = int(x + dx*0.2)
        new_y = int(y + dy*0.2)

        track_point = [new_x, new_y, 30, 30]

        # 绘制跟踪点
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