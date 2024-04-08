import cv2
import numpy as np

# 读取图像
img = cv2.imread('img/x.jpg')

# 转换为灰度图像
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 高斯滤波去噪
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# 使用Canny算子进行边缘检测
edges = cv2.Canny(blur, 100, 200)

# 查找轮廓
contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# 遍历轮廓
for cnt in contours:
    # 计算轮廓的面积和周长
    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)

    # 设置阈值,过滤掉小轮廓
    if area > 1000 and perimeter > 200:
        # 近似多边形
        approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)

        # 如果是矩形,则绘制边框
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 绘制四边形的边框
            cv2.drawContours(img, [approx], 0, (255, 0, 0), 2)

# 显示原始图像和带边框的图像
cv2.imshow('Original', img)
cv2.imwrite('out/x-out.jpg', img)
cv2.waitKey(0)
cv2.destroyAllWindows()