from flask import Flask, render_template, Response
import cv2

from stream import ThreadedCamera

app = Flask(__name__)

def generate_frames():
    # 320x240 640x480 960x720 1280x720 1920x1080
    url = 'http://192.168.100.4:4747/video?640x480'
    stream = ThreadedCamera(url)

    while True:
        frame = stream.frame
        if frame is not None:
            processed_frame = stream.process_frame(frame)
            # 将处理后的帧编码为JPEG格式
            ret, jpeg_buffer = cv2.imencode('.jpg', processed_frame)

            # 拼接MJPEG帧并返回
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg_buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)