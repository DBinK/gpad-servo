import cv2
import numpy as np

def calculate_intersection(segment1, segment2):
    x1, y1 = segment1[0]
    x2, y2 = segment1[1]
    x3, y3 = segment2[0]
    x4, y4 = segment2[1]

    dx1 = x2 - x1
    dx2 = x4 - x3
    dy1 = y2 - y1
    dy2 = y4 - y3

    det = dx1 * dy2 - dx2 * dy1

    if det == 0:
        # 线段平行或共线
        return None
    else:
        dx3 = x1 - x3
        dy3 = y1 - y3

        det1 = dx1 * dy3 - dx3 * dy1
        det2 = dx2 * dy3 - dx3 * dy2

        if det1 == 0 and det2 == 0:
            # 线段共线
            return None
        elif det1 == 0 or det2 == 0:
            # 线段平行
            return None
        else:
            s = det1 / det
            t = det2 / det

            if 0 <= s <= 1 and 0 <= t <= 1:
                # 计算交点坐标
                intersection_x = x1 + (dx1 * t)
                intersection_y = y1 + (dy1 * t)
                return (intersection_x, intersection_y)
            else:
                # 线段相交但交点不在线段上
                return None

# 示例使用
segment1 = ((1, 1), (4, 4))
segment2 = ((1, 4), (4, 1))
intersection = calculate_intersection(segment1, segment2)
print(intersection)

# 读取图像
img = cv2.imread('img/w2.jpg')

# 转换为灰度图像
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 高斯滤波去噪
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# 使用Canny算子进行边缘检测
edges = cv2.Canny(blur, 100, 200)

# 查找轮廓
contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# 初始化最大周长和对应的轮廓
max_perimeter = 0
max_cnt = None

# 遍历轮廓
for cnt in contours:
    # 计算轮廓的面积和周长
    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)

    # 设置阈值,过滤掉小轮廓
    if area > 1000 and perimeter > 200:
        # 如果当前轮廓的周长大于最大周长
        if perimeter > max_perimeter:
            max_perimeter = perimeter
            max_cnt = cnt

# 如果找到周长最大的轮廓
if max_cnt is not None:
    # 近似多边形
    approx = cv2.approxPolyDP(max_cnt, 0.02 * max_perimeter, True)

    # 如果是四边形,则绘制边框
    if len(approx) == 4:
        x, y, w, h = cv2.boundingRect(approx)
        # 绘制四边形的边框
        cv2.drawContours(img, [approx], 0, (255, 0, 0), 2)

        # 计算四边形的四个顶点坐标
        vertices = approx.reshape(4, 2)
        print(vertices)

        # 计算两个对角线的交点
        segment1 = (tuple(vertices[0]), tuple(vertices[2]))
        segment2 = (tuple(vertices[1]), tuple(vertices[3]))

        intersection = calculate_intersection(segment1, segment2)

        # 绘制交点和坐标
        if intersection is not None:
            cv2.circle(img, (int(intersection[0]), int(intersection[1])), 5, (255, 0, 0), -1)
            cv2.putText(img, f'({int(intersection[0])}, {int(intersection[1])})', (int(intersection[0])+5, int(intersection[1])-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        # 绘制每个顶点的坐标
        for i, vertex in enumerate(vertices):
            cv2.putText(img, f'({vertex[0]}, {vertex[1]})', (vertex[0]+5, vertex[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        # 绘制对角线
        cv2.line(img, (vertices[0][0], vertices[0][1]), (vertices[2][0], vertices[2][1]), (0, 255, 0), 1)
        cv2.line(img, (vertices[1][0], vertices[1][1]), (vertices[3][0], vertices[3][1]), (0, 255, 0), 1)

        # 输出交点的坐标
        if intersection is not None:
            print(f'Intersection coordinates: ({intersection[0]}, {intersection[1]})')

# 显示的图像
cv2.imshow('final', img)
cv2.imwrite('out/x-out.jpg', img)
cv2.waitKey(0)
cv2.destroyAllWindows()