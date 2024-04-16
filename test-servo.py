import cv2
import cam
import time

#URL = 0
URL = 'http://192.168.100.4:8080/video/mjpeg'
TRACK_SIZE = 30
SLEEP_DURATION_SEC = 0.02


kp = 0.1  # 比例增益
kd = 0.0  # 微分增益

def main():
    # 初始化摄像头
    cap = cv2.VideoCapture(URL)
    if not cap.isOpened():
        raise RuntimeError("Failed to open video capture device.")

    try:
        target_x, target_y = 100, 100
        track_point = [target_x, target_y, TRACK_SIZE, TRACK_SIZE]

        tracking_enabled = True

        while True:
            # 读取每一帧图像
            ret, frame = cap.read()

            if URL == 0:
                frame = cv2.flip(frame, 1)

            if not ret:
                print("Failed to read a frame from the video capture device.")
                continue

            red_point, _ = cam.find_point(frame)

            if red_point[0] != 0:
                frame = cam.draw_point(frame, red_point)

                if tracking_enabled:
                    # 启动 PD 控制算法
                    tracked_x, tracked_y = red_point[0], red_point[1]
                    dx = tracked_x - target_x
                    dy = tracked_y - target_y
                    target_x += int(dx * kp + dx * kd)
                    target_y += int(dy * kp + dy * kd)
                    track_point = [target_x, target_y, TRACK_SIZE, TRACK_SIZE]

                    # 到达指定误差范围后，停止追踪
                    if abs(dx) < 5 and abs(dy) < 5:
                        tracking_enabled = False

            frame = cam.draw_point(frame, track_point, bgr = (255, 0, 0))

            # 显示图像
            cv2.imshow('VIDEO', frame)

            # 处理键盘事件
            key = cv2.waitKey(1) & 0xFF
            if key == ord('t'):
                tracking_enabled = not tracking_enabled
            elif key == ord('q'):
                break

            time.sleep(SLEEP_DURATION_SEC)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # 释放资源并关闭窗口
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()