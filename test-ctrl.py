import cv2
import cam
from time import sleep

url = 3

TRACK_SIZE = 30
SLEEP_DURATION = 0.2

def main():
    # 初始化摄像头
    vcap = cv2.VideoCapture(url)
    if not vcap.isOpened():
        raise RuntimeError("Failed to open video capture device.")

    try:
        x, y = 100, 100
        track = True

        while True:
            # 读取每一帧图像
            ret, frame = vcap.read()
            if not ret:
                print("Failed to read a frame from the video capture device.")
                continue

            red_point, _ = cam.find_point(frame)

            if red_point[0] != 0:
                frame = cam.draw_point(frame, red_point)
            
            if track:
                r_x, r_y = red_point[0], red_point[1]
                dx = r_x - x
                dy = r_y - y
                x = int(x + dx * 0.2)
                y = int(y + dy * 0.2)
                track_point = [x, y, TRACK_SIZE, TRACK_SIZE]
                frame = cam.draw_point(frame, track_point)

            # 显示图像
            cv2.imshow('VIDEO', frame)

            # 处理键盘事件
            key = cv2.waitKey(1) & 0xFF
            if key == ord('t'):
                track = not track
            if key == ord('q'):
                break

            sleep(SLEEP_DURATION)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # 释放资源并关闭窗口
        vcap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()