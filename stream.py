import cv2
import numpy as np
import urllib.request

stream = urllib.request.urlopen('http://192.168.50.4:4747/video?640x480')
bytes = b''

while True:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')  # frame starting
    b = bytes.find(b'\xff\xd9')  # frame ending
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow('image', img)
        if cv2.waitKey(1) == 27:
            cv2.destroyAllWindows()
            break 