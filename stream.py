import cv2

# 打开MJPEG流
cap = cv2.VideoCapture('http://192.168.50.4:4747/video?640x480')

while True:
    # 读取一帧
    ret, frame = cap.read()

    # 检查是否成功读取
    if ret:
        # 显示帧
        cv2.imshow('MJPEG Stream', frame)

        # 等待0.1秒（单位：秒）
        cv2.waitKey(100)

# 关闭流
cap.release()