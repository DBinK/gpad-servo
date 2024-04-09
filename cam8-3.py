import cv2
import numpy as np
def calculate_intersection(vertices):
    x1, y1 = vertices[0]
    x2, y2 = vertices[2]
    x3, y3 = vertices[1]
    x4, y4 = vertices[3]

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

""" # 示例使用
line1 = ((1, 1), (4, 4))
line2 = ((1, 4), (4, 1))
intersection = calculate_intersection(line1, line2)
print(intersection) """

def shrink_rectangle(vertices, center_x, center_y, multiple):
    """
    已知四边形四个顶点坐标和中心点坐标，计算缩小 multiple 倍后的四边形坐标
    """
    new_vertices = []

    for vertex in vertices:
        new_x = int(center_x + (vertex[0] - center_x) * multiple)
        new_y = int(center_y + (vertex[1] - center_y) * multiple)
        new_vertices.append([new_x, new_y])

    return np.array(new_vertices, dtype=np.int32)

img = cv2.imread('img/rg.jpg')                # 读取图像
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度图像
blur = cv2.GaussianBlur(gray, (5, 5), 0)      # 高斯滤波去噪
edges = cv2.Canny(blur, 100, 200)             # 使用Canny算子进行边缘检测

contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓

# 初始化最大周长和对应的轮廓
max_perimeter = 0
max_cnt = None

# 遍历轮廓
for cnt in contours:
    # 计算轮廓的面积和周长
    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)
    print(area, perimeter)

    # 如果当前轮廓的周长大于最大周长
    if perimeter > max_perimeter:
        max_perimeter = perimeter
        max_cnt = cnt

if max_cnt is not None:   # 如果找到周长最大的轮廓
    approx = cv2.approxPolyDP(max_cnt, 0.02 * max_perimeter, True)  # 近似多边形

    if len(approx) == 4:  
        vertices = approx.reshape(4, 2)  # 将顶点值转换为 (4, 2) 的数组


        cv2.drawContours(img, [vertices], 0, (255, 0, 0), 2)  # 绘制四边形的边框

        # 绘制每个角点和坐标
        for i, vertex in enumerate(vertices):
            cv2.circle(img, (vertex[0], vertex[1]), 5, (0, 0, 255), -1)
            cv2.putText(img, f'({vertex[0]}, {vertex[1]})', (vertex[0]+5, vertex[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        # 绘制对角线
        cv2.line(img, (vertices[0][0], vertices[0][1]), (vertices[2][0], vertices[2][1]), (0, 255, 0), 1)
        cv2.line(img, (vertices[1][0], vertices[1][1]), (vertices[3][0], vertices[3][1]), (0, 255, 0), 1)

        """ # 计算两个对角线的交点
        line1 = (vertices[0], vertices[2])
        line2 = (vertices[1], vertices[3]) """
        intersection = calculate_intersection(vertices)

        # 绘制交点和坐标
        if intersection is not None:
            cv2.circle(img, (int(intersection[0]), int(intersection[1])), 5, (0, 0, 255), -1)
            cv2.putText(img, f'({int(intersection[0])}, {int(intersection[1])})', (int(intersection[0])+5, int(intersection[1])-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        # 输出交点的坐标
        if intersection is not None:
            print(f'交点的坐标: ({intersection[0]}, {intersection[1]})')

        # 绘制等比缩小后的图像
        new_vertices = shrink_rectangle(vertices, intersection[0], intersection[1], (0.5/0.6))
        cv2.drawContours(img, [new_vertices], 0, (255, 0, 0), 2)  # 绘制四边形的边框

        for vertex in new_vertices:
            cv2.circle(img, tuple(vertex), 5, (0, 0, 255), -1)
            cv2.putText(img, 
                        f'({int(vertex[0])}, {int(vertex[1])})', 
                        (int(vertex[0])+5, int(vertex[1])-5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 
                        1,  # 线宽度
                        cv2.LINE_AA)


# 显示的图像
cv2.imshow('final', img)
cv2.imwrite('out/x-out.jpg', img)
cv2.waitKey(0)
cv2.destroyAllWindows()