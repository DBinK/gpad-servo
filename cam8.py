import cv2
import numpy as np

from typing import List

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

    #_, threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #_, threshold = cv2.threshold(blur, 157, 255, cv2.THRESH_BINARY) # 二值化
    #edges = cv2.Canny(threshold, 10, 200)  # 使用Canny算子进行边缘检测
    edges = cv2.Canny(blur, 100, 200)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓
    return contours


def find_max_perimeter_contour(contours, max_allowed_perimeter, min_allowed_perimeter):
    # 输入参数校验
    if not contours or max_allowed_perimeter <= 0:
        raise ValueError("输入的轮廓列表不能为空，且最大允许周长必须为正数。")

    # 初始化最大周长及对应轮廓变量，以及标志位表示是否找到符合条件的轮廓
    max_perimeter = 0
    vertices = None

    # 遍历轮廓列表
    for cnt in contours:
        # 将当前轮廓近似为四边形
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)

        # 确保转换后的形状为四边形
        if len(approx) == 4:
            # 计算四边形周长
            perimeter = cv2.arcLength(approx, True)

            # 计算四边形角度
            cosines = []
            for i in range(4):
                p0 = approx[i][0]
                p1 = approx[(i + 1) % 4][0]
                p2 = approx[(i + 2) % 4][0]
                v1 = p0 - p1
                v2 = p2 - p1
                cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                angle = np.arccos(cosine_angle) * 180 / np.pi
                cosines.append(angle)

            perimeter_allowed = (perimeter <= max_allowed_perimeter) and (perimeter >= min_allowed_perimeter)
            # 若当前轮廓周长在允许范围内、大于当前最大周长且角度大于等于75度
            if perimeter_allowed and perimeter > max_perimeter and all(angle >= 75 for angle in cosines):
                max_perimeter = perimeter
                vertices = approx.reshape(4, 2)

    # 检查是否找到符合条件的轮廓
    if vertices is None:
        # 返回空列表代替None，或可选择抛出异常
        return None
    else:
        return vertices



def draw_contour_and_vertices(img: cv2.Mat, vertices: List[List[int]], scale: float) -> cv2.Mat:
    """
    在图像上绘制四边形的轮廓、顶点、对角线、交点，并等比缩小重新绘制。
    
    :param img: 输入的OpenCV图像
    :param vertices: 四边形的顶点列表，格式为[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    :param scale: 缩小比例
    :return: 绘制后的图像
    """

    try:   
        if vertices is not None:
            # 将四边形顶点列表转换为适合drawContours()的格式
            contour = np.array([vertices], dtype=np.int32)  # 创建一个二维numpy数组，形状为(1, N, 2)，其中N为顶点数
            cv2.drawContours(img, [contour], 0, (255, 0, 0), 2)  # 绘制四边形的边框
        else: 
            print("顶点无效或缺失,跳过轮廓绘制。")  

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
        
            # 绘制等比缩小后的图像
            new_vertices = shrink_rectangle(
                vertices, intersection[0], intersection[1], scale
            )
            cv2.drawContours(img, [new_vertices], 0, (255, 0, 0), 2)  # 绘制四边形的边框

            for vertex in new_vertices:
                cv2.circle(img, vertex, 5, (0, 0, 255), -1)
                cv2.putText(
                    img,
                    f"({int(vertex[0])}, {int(vertex[1])})",
                    (vertex[0] + 5, vertex[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 1, cv2.LINE_AA,
                )

    except Exception as e:
        print(f"绘制过程中发生错误: {e}")
    
    return img


if __name__ == "__main__":
    img = cv2.imread("img/rg.jpg")
    contours = preprocess_image(img)

    if contours is not None:
        vertices = find_max_perimeter_contour(contours, 10090*4, 880*4)
        img = draw_contour_and_vertices(img, vertices, (276 / 297)) # (0.5/0.6)

    if vertices is not None:
        print(f"四个顶点坐标: {vertices}")

    # 显示的图像
    cv2.imshow("final", img)
    cv2.imwrite("out/x-out.jpg", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
