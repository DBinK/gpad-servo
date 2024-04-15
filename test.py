import stream

# 320x240 640x480 960x720 1280x720 1920x1080
# url = 'http://192.168.100.4:4747/video?960x720'
url = 1 # 使用本地摄像头

cam = stream.ThreadedCamera(url)

while True:
    try:
        cam.show_frame()
    except AttributeError:
        pass