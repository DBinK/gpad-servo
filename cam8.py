import cv2
import numpy as np

def calculate_intersection(vertices):
    """
    计算四边形对角线的交点。

    参数:
    vertices: 一个包含四个顶点坐标的列表，每个顶点是一个二元组(x, y)。

    返回值:
    如果存在交点，返回交点的坐标(x, y)；如果不存在交点，返回None。
    """
    x1, y1 = vertices[0]
    x2, y2 = vertices[2]
    x3, y3 = vertices[1]
    x4, y4 = vertices[3]

    dx1, dy1 = x2 - x1, y2 - y1
    dx2, dy2 = x4 - x3, y4 - y3

    det = dx1 * dy2 - dx2 * dy1

    if det == 0 or (dx1 == 0 and dx2 == 0) or (dy1 == 0 and dy2 == 0):
        return None

    dx3, dy3 = x1 - x3, y1 - y3
    det1 = dx1 * dy3 - dx3 * dy1
    det2 = dx2 * dy3 - dx3 * dy2

    if det1 == 0 or det2 == 0:
        return None

    s = det1 / det
    t = det2 / det

    if 0 <= s <= 1 and 0 <= t <= 1:
        intersection_x = x1 + dx1 * t
        intersection_y = y1 + dy1 * t
        return int(intersection_x), int(intersection_y)
    else:
        return None


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

def preprocess_image(img):
    """
    对输入图像进行预处理，包括灰度转换、高斯模糊、Canny边缘检测，并返回边缘图像及其中的轮廓信息。
    参数:
        img (np.ndarray): 待处理图像
    返回:
        tuple: 包含以下元素的元组：
            - edges (np.ndarray): Canny边缘检测后的图像（灰度图像）
            - contours (list): 边缘图像中的轮廓信息列表
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度图像

    blur = cv2.GaussianBlur(gray, (5, 5), 0)  # 高斯滤波去噪

    _, threshold = cv2.threshold(blur, 2, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #_, threshold = cv2.threshold(blur, 233, 255, cv2.THRESH_BINARY) # 二值化

    edges = cv2.Canny(threshold, 100, 200)  # 使用Canny算子进行边缘检测
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
    """
    :param contour: 轮廓
    :param max_perimeter: 最大周长
    :return: 轮廓中心点坐标
    """
    if max_perimeter is not None:
        approx = cv2.approxPolyDP(contour, 0.02 * max_perimeter, True)  # 近似多边形

        if len(approx) == 4:  # 如果是四边形,计算四边形的四个顶点坐标并返回
            vertices = approx.reshape(4, 2)  
            print(vertices)
            return vertices

def draw_contour_and_vertices(img, vertices):
    """
    绘制轮廓和顶点和交点
    :param img: 输入图像
    :param vertices: 顶点坐标
    :return: 绘制后的图像
    """
    if vertices is not None:
        cv2.drawContours(img, [vertices], 0, (255, 0, 0), 2)  # 绘制四边形的边框

        for i, vertex in enumerate(vertices):  # 绘制每个角点和坐标
            cv2.circle(img, (vertex[0], vertex[1]), 5, (0, 0, 255), -1)
            cv2.putText(
                img,
                f"({vertex[0]}, {vertex[1]})",
                (vertex[0] + 5, vertex[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 1, cv2.LINE_AA,
            )

        cv2.line(  # 绘制对角线
            img,
            (vertices[0][0], vertices[0][1]),
            (vertices[2][0], vertices[2][1]),
            (0, 255, 0), 1,
        )
        cv2.line(
            img,
            (vertices[1][0], vertices[1][1]),
            (vertices[3][0], vertices[3][1]),
            (0, 255, 0), 1,
        )
        
        intersection = calculate_intersection(vertices)  # 计算两个对角线的交点

        # 绘制交点和坐标
        if intersection is not None:
            cv2.circle(
                img, (int(intersection[0]), int(intersection[1])), 5, (0, 0, 255), -1
            )
            cv2.putText(
                img,
                f"({int(intersection[0])}, {int(intersection[1])})",
                (int(intersection[0]) + 5, int(intersection[1]) - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 1, cv2.LINE_AA,
            )
            # 输出交点的坐标
            """ if intersection is not None:
                print(f"交点的坐标: ({intersection[0]}, {intersection[1]})") """
            
            """return img , intersection
    def draw_max_cnt_rectangle(img, vertices):  # 绘制等比缩小后的轮廓和顶点和交点

        if vertices is not None:
            img, intersection = draw_contour_and_vertices(img, vertices) """
        
            # 绘制等比缩小后的图像
            new_vertices = shrink_rectangle(
                vertices, intersection[0], intersection[1], (0.5 / 0.6)
            )
            cv2.drawContours(img, [new_vertices], 0, (255, 0, 0), 2)  # 绘制四边形的边框

            for vertex in new_vertices:
                cv2.circle(img, tuple(vertex), 5, (0, 0, 255), -1)
                cv2.putText(
                    img,
                    f"({int(vertex[0])}, {int(vertex[1])})",
                    (int(vertex[0]) + 5, int(vertex[1]) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 1, cv2.LINE_AA,
                )

            return img #, intersection


if __name__ == "__main__":
    img = cv2.imread("img/c.jpg")
    contours = preprocess_image(img)
    max_perimeter, max_cnt = find_max_perimeter_contour(contours)

    if max_cnt is not None:
        vertices = find_contour_xy(max_cnt, max_perimeter)
        draw_contour_and_vertices(img, vertices)

    if vertices is not None:
        print(f"四个顶点坐标: {vertices}")

    # 显示的图像
    cv2.imshow("final", img)
    cv2.imwrite("out/x-out.jpg", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
