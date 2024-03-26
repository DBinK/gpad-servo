import cv2
from flask import Flask, Response

app = Flask(__name__)

# 读取MJPEG流
cap = cv2.VideoCapture('http://192.168.50.40:4747/video?1920x1080')

def generate_frames():
    while True:
        ret, frame = cap.read()

        # 在画面中间绘制一个十字准星
        height, width, _ = frame.shape
        center_x = width // 2
        center_y = height // 2  
        line_length = 100 # 十字准星的长度
        cv2.line(frame, (center_x - line_length, center_y), (center_x + line_length, center_y), (0, 255, 0), 2)
        cv2.line(frame, (center_x, center_y - line_length), (center_x, center_y + line_length), (0, 255, 0), 2)

        # 将帧转换为JPEG格式
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # 生成带有十字准星的画面
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return Response(generate_frames(),
                mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()