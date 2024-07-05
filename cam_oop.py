
import cv2
import numpy as np
import sys
from loguru import logger

# 设置日志级别为 DEBUG
logger.remove()
logger.add(sys.stderr, level="DEBUG")  # 输出到stderr（默认是控制台），级别为DEBUG

class QuadDetector:
    def __init__(self, img, max_perimeter, min_perimeter, scale, min_angle=30):
        """
        @param img: 图像来源
        @param max_perimeter: 允许的最大周长
        @param min_perimeter: 允许的最小周长
        @param scale: 缩放比例
        """
        self.img = img
        self.max_perimeter = max_perimeter
        self.min_perimeter = min_perimeter
        self.scale = scale
        self.min_angle = min_angle

        self.vertices = None

    def preprocess_image(self):

        """
        对输入图像进行预处理, 包括灰度转换、高斯模糊、Canny边缘检测, 并返回其中的轮廓信息。
        """
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)  # 转换为灰度图像

        blur = cv2.GaussianBlur(gray, (1, 1), 0)  # 高斯滤波去噪

        # 减小曝光
        # exposure_adjusted = cv2.addWeighted(blur, 0.5, np.zeros(blur.shape, dtype=blur.dtype), 0, 50)

        # 增加对比度（直方图均衡化）
        # blur = cv2.convertScaleAbs(blur, alpha=0.5, beta=-50)
        # blur = cv2.convertScaleAbs(blur, alpha=1, beta=-120)
        
        # 二值化
        # _, blur = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # _, threshold = cv2.threshold(blur, 157, 255, cv2.THRESH_BINARY) # 二值化

        edges = cv2.Canny(blur, 50, 200)

        self.pre_img = edges

    def find_max_quad_vertices(self):
        """
        在预处理后的图像中寻找具有最大周长的四边形，并返回顶点坐标
        """
        contours, _ = cv2.findContours(self.pre_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓

        logger.debug(f'contours cnt: {len(contours)}')

        max_perimeter = 0

        # 遍历轮廓列表
        for cnt in contours:
            # 将当前轮廓近似为四边形
            approx = cv2.approxPolyDP(cnt, 0.09 * cv2.arcLength(cnt, True), True)

            # 确保转换后的形状为四边形
            if len(approx) == 4:
                # 计算四边形周长
                perimeter = cv2.arcLength(approx, True)
                perimeter_allowed = (perimeter <= self.max_perimeter) and (perimeter >= self.min_perimeter)
                # cv2.drawContours(img, [approx], 0, (255, 0, 0), 2)

                if perimeter_allowed and perimeter > max_perimeter:
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
                        
                    # 若当前轮廓周长在允许范围内、大于当前最大周长且角度大于 min_angle
                    if all(angle >= self.min_angle for angle in cosines):
                        max_perimeter = perimeter
                        self.vertices = approx.reshape(4, 2)

        logger.info(f"Found vertices: {self.vertices}")

        return self.vertices
        
    def detect(self):
        """
        对预处理后的图像进行轮廓检测，并返回检测到的轮廓信息。
        """
        self.preprocess_image()
        vertices = self.find_max_quad_vertices()
        return vertices
    
    def draw(self):
        """
        在给定的图像上绘制轮廓和顶点坐标。
        """
        # 绘制轮廓
        cv2.drawContours(img, [self.vertices], 0, (255, 0, 0), 2)

        for _, vertex in enumerate(self.vertices):  # 绘制每个角点和坐标
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
            (self.vertices[0][0], self.vertices[0][1]),
            (self.vertices[2][0], self.vertices[2][1]),
            (0, 255, 0), 1,
        )
        cv2.line(
            img,
            (self.vertices[1][0], self.vertices[1][1]),
            (self.vertices[3][0], self.vertices[3][1]),
            (0, 255, 0), 1,
        )
        

if __name__ == '__main__':


    print("开始")
    
    img = cv2.imread("img/rgb.jpg")

    detector = QuadDetector(img, 100000, 100, 0.5)
    detector.detect()
    detector.draw()

    cv2.imshow("img", img)
    cv2.waitKey(0)