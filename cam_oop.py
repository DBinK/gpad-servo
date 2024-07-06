
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
        self.img = img.copy()
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
    
    def find_scale_quad_vertices(self):
        """
        计算按比例缩放后的四边形
        """
        def persp_trans(img, vertices):
            # 对四边形顶点坐标进行排序
            rect = np.zeros((4, 2), dtype="float32")
            rect[0] = vertices[0]
            rect[1] = vertices[3]
            rect[2] = vertices[2]
            rect[3] = vertices[1]

            height, width = img.shape[:2]  # 获取图像的高度和宽度

            # 定义目标矩形的顶点坐标，即变换后的图像矩形框
            dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32")

            # 计算透视变换矩阵
            M = cv2.getPerspectiveTransform(rect, dst)
            inv_M = np.linalg.inv(M)

            # 返回变换后的图像及变换矩阵
            return M, inv_M
        
        def shrink_rectangle_new(img, scale):
            """
            参数:
            img: 一个数组，代表图像
            scale: 缩小的比例因子，表示新矩形的大小是原矩形大小的scale倍。

            返回值:
            返回一个类型为numpy.int32的二维数组，包含四个点的坐标，这四个点分别代表缩小后矩形的四个顶点。
            """

            height, width = img.shape[:2]

            rectangle_vertices = [[],[],[],[]]
            
            rectangle_vertices[0] = [0, 0]
            rectangle_vertices[1] = [0, height]
            rectangle_vertices[2] = [width, height]
            rectangle_vertices[3] = [width, 0]

            #print (rectangle_vertices)

            center_x = width // 2
            center_y = height // 2

            small_vertices = []

            for vertex in rectangle_vertices:
                new_x = int(center_x + (vertex[0] - center_x) * scale)
                new_y = int(center_y + (vertex[1] - center_y) * scale)
                small_vertices.append([new_x, new_y])

            #print (small_vertices)

            return np.array(small_vertices, dtype=np.int32)


        def inv_trans_vertices(small_vertices, inv_M):
            """
            反变换顶点集合
            
            参数:
            small_vertices: 一个二维数组，代表待变换的顶点集合，每个顶点为2D坐标。
            inv_M: 一个4x4的矩阵，代表待应用的逆变换矩阵。
            
            返回值:
            一个二维数组，表示应用逆变换后的顶点集合，顶点仍为2D坐标，但取整至最接近的整数。
            """
            
            vertices_array = np.array(small_vertices, dtype=np.float32)
            vertices_homo = np.concatenate([vertices_array, np.ones((vertices_array.shape[0], 1))], axis=1)
            
            inv_trans_vertices_homo = np.dot(inv_M, vertices_homo.T).T
            inv_trans_vertices = inv_trans_vertices_homo[:, :2] / inv_trans_vertices_homo[:, 2, None]
            
            inv_trans_vertices_int = inv_trans_vertices.astype(int)

            return inv_trans_vertices_int
        
        def draw_warped_image(img, M, inv_M):    # 用于检查变换效果

            height, width = img.shape[:2]  # 获取图像的高度和宽度

            # 应用透视变换到图像上
            warped_image = cv2.warpPerspective(img, M, (width, height))

            # 应用逆透视变换到图像
            inv_warped_image = cv2.warpPerspective(warped_image, inv_M,  (width, height))
            
            return warped_image, inv_warped_image
        
        _, inv_M = persp_trans(self.img, self.vertices)  # 获取透视变换矩阵
            
        small_vertices = shrink_rectangle_new(self.img, self.scale)  # 缩小矩形

        self.scale_vertices = inv_trans_vertices(small_vertices, inv_M)

        logger.info(f"Found scale vertices: {self.scale_vertices}")

        return self.scale_vertices

        
    def detect(self):
        """
        对预处理后的图像进行轮廓检测，并返回检测到的轮廓信息。
        """
        self.preprocess_image()
        vertices = self.find_max_quad_vertices()
        scale_vertices = self.find_scale_quad_vertices()

        return vertices, scale_vertices
    
    def draw(self):
        """
        在给定的图像上绘制轮廓和顶点坐标。
        """
        def draw_point_text(img, x, y, bgr = ( 0, 0, 255)): #绘制一个点，并显示其坐标。
            cv2.circle(img, (x, y), 5, bgr, -1)
            cv2.putText(
                img,
                f"({x}, {y})",
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 1, cv2.LINE_AA,
            )

        def draw_lines_points(img, vertices, bold=2):
            # 绘制轮廓
            cv2.drawContours(img, [vertices], 0, (255, 0, 0), bold)

            for _, vertex in enumerate(vertices):  # 绘制每个角点和坐标
                draw_point_text(img, vertex[0], vertex[1])
            
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
            return img

        img_drawed = draw_lines_points(self.img, self.vertices)
        img_drawed = draw_lines_points(img_drawed, self.scale_vertices)

        return img_drawed


if __name__ == '__main__':


    print("开始")
    
    img = cv2.imread("img/rgb.jpg")
    

    detector = QuadDetector(img, 100000, 100, 500/600)
    detector.detect()
    img_ = detector.draw()

    cv2.imshow("img", img)
    cv2.imshow("img_", img_)
    cv2.waitKey(0)