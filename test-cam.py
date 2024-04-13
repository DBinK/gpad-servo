import cv2
import numpy as np

# 增加饱和度函数
def increase_saturation(img, factor):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# 读取图像
img = cv2.imread('img/i.png')

# 高斯模糊
blurred = cv2.GaussianBlur(img, (5, 5), 0)

# 增加饱和度
blurred = increase_saturation(blurred, 8)

# 计算图像梯度
edges = cv2.Canny(blurred, 100, 200)


# 显示结果
cv2.imshow('Original Image', img)
cv2.imshow('Preprocessed Image', blurred)
cv2.imshow('Edges', edges)
cv2.waitKey(0)
cv2.destroyAllWindows()


