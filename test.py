import cv2
#import numpy as np

def calculate_intersection(line1, line2):
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]

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


def shrink_rectangle(x1, y1, x2, y2, x3, y3, x4, y4, center_x, center_y, multiple):
    """
    已知四边形四个顶点坐标和中心点坐标,计算缩小 multiple 倍后的四边形坐标
    """
    # 计算缩小后的四个顶点坐标
    new_x1 = int(center_x + (x1 - center_x) * multiple)
    new_y1 = int(center_y + (y1 - center_y) * multiple)
    new_x2 = int(center_x + (x2 - center_x) * multiple)
    new_y2 = int(center_y + (y2 - center_y) * multiple)
    new_x3 = int(center_x + (x3 - center_x) * multiple)
    new_y3 = int(center_y + (y3 - center_y) * multiple)
    new_x4 = int(center_x + (x4 - center_x) * multiple)
    new_y4 = int(center_y + (y4 - center_y) * multiple)

    return int(new_x1), int(new_y1), int(new_x2), int(new_y2), int(new_x3), int(new_y3), int(new_x4), int(new_y4)

def preprocess_image(image_path):
    """
    对输入图像进行预处理，包括灰度转换、高斯模糊、Canny边缘检测，并返回边缘图像及其中的轮廓信息。

    参数:
        image_path (str): 待处理图像的路径

    返回:
        tuple: 包含以下元素的元组：
            - edges (np.ndarray): Canny边缘检测后的图像（灰度图像）
            - contours (list): 边缘图像中的轮廓信息列表
    """
    global img
    img = cv2.imread(image_path)  # 读取图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度图像
    blur = cv2.GaussianBlur(gray, (5, 5), 0)  # 高斯滤波去噪
    edges = cv2.Canny(blur, 100, 200)  # 使用Canny算子进行边缘检测
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓

    return contours

def find_max_perimeter_contour(contours):
    """
    给定一组轮廓列表，该函数用于识别具有最大周长的轮廓，并返回最大周长值及对应的轮廓。

    参数:
    - contours (list): 一个轮廓列表，其中每个轮廓表示为包含(x, y)坐标的Numpy数组。

    返回:
    tuple: 包含以下内容的元组：
      - max_perimeter (float): 输入轮廓中所有轮廓的最大周长。
      - max_cnt (Numpy数组): 具有最大周长的轮廓。
    """
    # 初始化最大周长及对应轮廓变量
    max_perimeter = 0
    max_cnt = None

    # 遍历轮廓列表
    for cnt in contours:
        # 计算当前轮廓的面积和周长
        # area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)

        # 若当前轮廓周长大于当前最大周长
        if perimeter > max_perimeter:
            max_perimeter = perimeter
            max_cnt = cnt

    # 返回最大周长及其对应的轮廓
    return max_perimeter, max_cnt

def find_contour_xy(contour, max_perimeter):
    approx = cv2.approxPolyDP(contour, 0.02 * max_perimeter, True)  # 近似多边形

    if len(approx) == 4:  # 如果是四边形,计算四边形的四个顶点坐标并返回
        cv2.drawContours(img, [approx], 0, (255, 0, 0), 2)  # 绘制四边形的边框
        vertices = approx.reshape(4, 2)  # 计算四边形的四个顶点坐标并返回
        return vertices


# 绘制每个顶点的坐标
for i, vertex in enumerate(vertices):
    cv2.circle(img, (vertex[0], vertex[1]), 5, (0, 0, 255), -1)
    cv2.putText(img, f'({vertex[0]}, {vertex[1]})', (vertex[0]+5, vertex[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

# 绘制对角线
cv2.line(img, (vertices[0][0], vertices[0][1]), (vertices[2][0], vertices[2][1]), (0, 255, 0), 1)
cv2.line(img, (vertices[1][0], vertices[1][1]), (vertices[3][0], vertices[3][1]), (0, 255, 0), 1)

# 计算两个对角线的交点
line1 = (vertices[0], vertices[2])
line2 = (vertices[1], vertices[3])
intersection = calculate_intersection(line1, line2)

# 绘制交点和坐标
if intersection is not None:
    cv2.circle(img, (int(intersection[0]), int(intersection[1])), 5, (0, 0, 255), -1)
    cv2.putText(img, f'({int(intersection[0])}, {int(intersection[1])})', (int(intersection[0])+5, int(intersection[1])-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
# 输出交点的坐标
if intersection is not None:
    print(f'交点的坐标: ({intersection[0]}, {intersection[1]})')

x1,y1 = vertices[0]
x2,y2 = vertices[1]
x3,y3 = vertices[2]
x4,y4 = vertices[3]

# 绘制等比缩小后的图像
new_x1, new_y1, new_x2, new_y2, new_x3, new_y3, new_x4, new_y4 = shrink_rectangle(x1, y1, x2, y2, x3, y3, x4, y4, intersection[0], intersection[1], (0.5/0.6))

# 绘制连接线
cv2.line(img, (new_x1, new_y1), (new_x2, new_y2), (0, 255, 0), 1)
cv2.line(img, (new_x2, new_y2), (new_x3, new_y3), (0, 255, 0), 1)
cv2.line(img, (new_x3, new_y3), (new_x4, new_y4), (0, 255, 0), 1)
cv2.line(img, (new_x4, new_y4), (new_x1, new_y1), (0, 255, 0), 1)

cv2.circle(img, (new_x1, new_y1), 5, (0, 0, 255), -1)
cv2.circle(img, (new_x2, new_y2), 5, (0, 0, 255), -1)
cv2.circle(img, (new_x3, new_y3), 5, (0, 0, 255), -1)
cv2.circle(img, (new_x4, new_y4), 5, (0, 0, 255), -1)

cv2.putText(img, f'({int(new_x1)}, {int(new_x1)})', (int(new_x1)+5, int(new_y1)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
cv2.putText(img, f'({int(new_x2)}, {int(new_y2)})', (int(new_x2)+5, int(new_y2)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
cv2.putText(img, f'({int(new_x3)}, {int(new_y3)})', (int(new_x3)+5, int(new_y3)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
cv2.putText(img, f'({int(new_x4)}, {int(new_y4)})', (int(new_x4)+5, int(new_y4)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

# 显示的图像
cv2.imshow('final', img)
cv2.imwrite('out/x-out.jpg', img)
cv2.waitKey(0)
cv2.destroyAllWindows()