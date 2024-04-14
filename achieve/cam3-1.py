import cv2
import numpy as np

# 读取图像
image = cv2.imread('img/w1.jpg')

# 将图像转换为灰度图
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 使用Canny边缘检测器检测图像边缘
edged = cv2.Canny(gray, 30, 200)

# 寻找图像中的轮廓
contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 初始化变量以存储最长对角线的信息
max_diagonal_length = 0
max_diagonal_points = []

# 遍历轮廓
for contour in contours:
    # 计算轮廓的周长
    perimeter = cv2.arcLength(contour, True)
    # 使用逼近多边形方法来逼近轮廓
    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
    # 如果逼近的多边形有4个顶点，则认为是四边形
    if len(approx) == 4:
        # 绘制检测到的四边形
        cv2.drawContours(image, [approx], -1, (0, 255, 0), 3)
        # 计算四边形的对角线长度和对角线的交点
        for i in range(4):
            for j in range(i+1, 4):
                pt1 = tuple(approx[i][0])
                pt2 = tuple(approx[j][0])
                diagonal_length = np.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)
                if diagonal_length > max_diagonal_length:
                    max_diagonal_length = diagonal_length
                    max_diagonal_points = [pt1, pt2]

# 计算对角线的交点作为四边形的中心点坐标
center_x = (max_diagonal_points[0][0] + max_diagonal_points[1][0]) // 2
center_y = (max_diagonal_points[0][1] + max_diagonal_points[1][1]) // 2

# 在图像上绘制对角线和中心点

cv2.line(image, max_diagonal_points[0], max_diagonal_points[1], (0, 255, 0), 2)
cv2.circle(image, (center_x, center_y), 5, (0, 0, 255), -1)

# 显示原始图像和检测到的四边形以及中心点
cv2.imshow('Detected Quadrilateral with Center', image)
cv2.waitKey(0)
cv2.destroyAllWindows()


# 保存结果图像
cv2.imwrite('out.jpg', image)