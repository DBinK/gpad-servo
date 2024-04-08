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

        # 如果是四边形,则绘制边框
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 绘制四边形的边框
            cv2.drawContours(img, [approx], 0, (255, 0, 0), 2)

            # 计算四边形的四个顶点坐标
            vertices = approx.reshape(4, 2)

            # 绘制每个顶点的坐标
            for i, vertex in enumerate(vertices):
                cv2.putText(img, f'({vertex[0]}, {vertex[1]})', (vertex[0]+5, vertex[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            # 绘制对角线
            cv2.line(img, (vertices[0][0], vertices[0][1]), (vertices[2][0], vertices[2][1]), (0, 255, 0), 2)
            cv2.line(img, (vertices[1][0], vertices[1][1]), (vertices[3][0], vertices[3][1]), (0, 255, 0), 2)

            # 计算对角线的交点
            (x1, y1), (x2, y2) = vertices[0], vertices[2]
            (x3, y3), (x4, y4) = vertices[1], vertices[3]
            intersectionX = (x1 * y2 - y1 * x2) / (y3 - y4) + x3
            intersectionY = (x3 * y4 - y3 * x4) / (x1 - x2) + y1

            # 绘制对角线的交点
            cv2.circle(img, (int(intersectionX), int(intersectionY)), 5, (0, 255, 0), -1)
            cv2.putText(img, f'({int(intersectionX)}, {int(intersectionY)})', (int(intersectionX)+5, int(intersectionY)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

# 显示的图像
cv2.imshow('final', img)
cv2.imwrite('out/x-out.jpg', img)
cv2.waitKey(0)
cv2.destroyAllWindows()