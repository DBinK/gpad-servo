import cv2
import numpy as np

# 增加饱和度函数
def increase_saturation(img, factor):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# 读取图像
img = cv2.imread('img/i.png')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度图像

blur = cv2.GaussianBlur(gray, (5, 5), 0)  # 高斯滤波去噪

"""     # 颜色量化
div = 16
blur = blur // div * div + div // 2 """

# 减小曝光
#exposure_adjusted = cv2.addWeighted(blur, 0.5, np.zeros(blur.shape, dtype=blur.dtype), 0, 50)

# 增加对比度（直方图均衡化）
#blur = cv2.convertScaleAbs(blur, alpha=0.5, beta=-50)
blur = cv2.convertScaleAbs(blur, alpha=1, beta=-120)

#_, threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#_, threshold = cv2.threshold(blur, 157, 255, cv2.THRESH_BINARY) # 二值化
#edges = cv2.Canny(threshold, 10, 200)  # 使用Canny算子进行边缘检测
edges = cv2.Canny(blur, 20, 200)


# 显示结果
cv2.imshow('Original Image', img)
cv2.imshow('Preprocessed Image', blur)
cv2.imshow('Edges', edges)
cv2.waitKey(0)
cv2.destroyAllWindows()

