import cv2 
import numpy as np

# 读取图像
image = cv2.imread('a.jpg')

# 将图像转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 应用二值阈值处理
ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# 使用findContours()函数检测轮廓
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 绘制轮廓
cv2.drawContours(image, contours, -1, (0, 0, 255), 2)

# 在方框的四个角位置绘制蓝色圆圈
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    cv2.circle(image, (x, y), 5, (255, 0, 0), -1)
    cv2.circle(image, (x + w, y), 5, (255, 0, 0), -1)
    cv2.circle(image, (x, y + h), 5, (255, 0, 0), -1)
    cv2.circle(image, (x + w, y + h), 5, (255, 0, 0), -1)

# 显示结果图像
cv2.namedWindow("Result", cv2.WINDOW_NORMAL)

cv2.resizeWindow("Result", 1280, 720)
cv2.imshow('Result', image)
cv2.waitKey(0)
cv2.destroyAllWindows()