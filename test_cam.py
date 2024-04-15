
import cv2
import cam8

url = 'rtsp://192.168.100.4:8080/video/h264'
# 打开RTSP流
vcap = cv2.VideoCapture(url)

while True:
    # 读取每一帧图像
    ret, frame = vcap.read()

    red_point,green_point = cam8.find_point(frame)

    if red_point[0] != 0:
        frame = cam8.draw_point(frame,red_point)

    if green_point[0] != 0:
        frame = cam8.draw_point(frame,green_point)
    # 显示图像
    cv2.imshow('VIDEO', frame)

    # 按键盘上的任意键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
vcap.release()
cv2.destroyAllWindows()