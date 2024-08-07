
import cv2
import numpy as np
import sys
from loguru import logger

# 设置日志级别为 DEBUG
logger.remove()
#logger.add(sys.stderr, level="DEBUG")  # 输出到stderr（默认是控制台），级别为DEBUG
logger.add(sys.stderr, level="INFO")  # 输出到stderr（默认是控制台），级别为DEBUG


class QuadDetector:
    def __init__(self, max_perimeter, min_perimeter, scale, min_angle=30, line_seg_num=4):
        """
        @param img: 图像来源
        @param max_perimeter: 允许的最大周长
        @param min_perimeter: 允许的最小周长
        @param scale: 缩放比例
        @param min_angle: 允许的最小角度
        @param line_seg_num: 分段数量
        """
        self.img = None

        self.max_perimeter = max_perimeter
        self.min_perimeter = min_perimeter
        self.scale         = scale
        self.min_angle     = min_angle
        self.line_seg_num  = line_seg_num

        self.vertices       = None
        self.scale_vertices = None
        self.intersection   = None
        self.points_list    = None

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
                    else:
                        self.vertices = None

        logger.info(f"Found vertices: {self.vertices.tolist()}")
        
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
            @param img: 输入图像, 为了获得图像高宽
            @param scale: 缩放比例
            @return: 中心缩放后的顶点坐标
            """

            height, width = img.shape[:2]

            rectangle_vertices = [[],[],[],[]]
            
            rectangle_vertices[0] = [0, 0]
            rectangle_vertices[1] = [0, height]
            rectangle_vertices[2] = [width, height]
            rectangle_vertices[3] = [width, 0]

            center_x = width // 2
            center_y = height // 2

            small_vertices = []

            for vertex in rectangle_vertices:
                new_x = int(center_x + (vertex[0] - center_x) * scale)
                new_y = int(center_y + (vertex[1] - center_y) * scale)
                small_vertices.append([new_x, new_y])

            return np.array(small_vertices, dtype=np.int32)


        def inv_trans_vertices(small_vertices, inv_M):
            """
            @param small_vertices: 缩放后的顶点坐标
            @param inv_M: 逆变换矩阵
            @return: 逆变换后的顶点坐标
            """
            
            vertices_array = np.array(small_vertices, dtype=np.float32)
            vertices_homo = np.concatenate([vertices_array, np.ones((vertices_array.shape[0], 1))], axis=1)
            
            inv_trans_vertices_homo = np.dot(inv_M, vertices_homo.T).T
            inv_trans_vertices = inv_trans_vertices_homo[:, :2] / inv_trans_vertices_homo[:, 2, None]
            
            inv_trans_vertices_int = inv_trans_vertices.astype(int)

            return inv_trans_vertices_int
        
        def draw_warped_image(img, M, inv_M):    # 用于检查变换效果
            """
            @param img: 输入图像
            @param M: 透视变换矩阵
            @param inv_M: 逆透视变换矩阵
            @return: 透视变换后的图像
            """
            height, width = img.shape[:2]  # 获取图像的高度和宽度

            # 应用透视变换到图像上
            warped_image = cv2.warpPerspective(img, M, (width, height))

            # 应用逆透视变换到图像
            inv_warped_image = cv2.warpPerspective(warped_image, inv_M,  (width, height))
            
            return warped_image, inv_warped_image
        
        _, inv_M            = persp_trans(self.img, self.vertices)  # 获取透视变换矩阵
        small_vertices      = shrink_rectangle_new(self.img, self.scale)  # 缩小矩形
        self.scale_vertices = inv_trans_vertices(small_vertices, inv_M)

        logger.debug(f"Found scale vertices: {self.scale_vertices}")

        return self.scale_vertices

    def segment_line(self, scale_vertices=None, line_seg_num=None):
        """
        根据给定的线段数，将四边形每条边的等分点集合返回
        """
        if scale_vertices is None:
            scale_vertices = self.scale_vertices

        if line_seg_num is None:
            line_seg_num = self.line_seg_num
        
        def average_points(point1, point2, N):
            """
            根据两个给定点和分段数N, 计算这两个点之间等分的坐标点列表。
            """
            delta_x = (point2[0] - point1[0]) / N
            delta_y = (point2[1] - point1[1]) / N
            
            points_list = []
            
            for i in range(N+1):
                x = point1[0] + delta_x * i
                y = point1[1] + delta_y * i
                points_list.append([x, y])
            
            return points_list

        points_0 = average_points(scale_vertices[0], scale_vertices[1], line_seg_num)
        points_1 = average_points(scale_vertices[1], scale_vertices[2], line_seg_num)
        points_2 = average_points(scale_vertices[2], scale_vertices[3], line_seg_num)
        points_3 = average_points(scale_vertices[3], scale_vertices[0], line_seg_num)

        self.points_list = [points_0, points_1, points_2, points_3]
        logger.debug(f"Found points list: {self.points_list}")

        return self.points_list
    
    def calculate_intersection(self, vertices=None):
        """
        @description: 计算四边形对角线的交点。
        @param vertices: 输入的顶点坐标
        @return: 返回交点坐标
        """
        if vertices is None:
            vertices = self.vertices

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
            intersection_x = int(x1 + dx1 * t)
            intersection_y = int(y1 + dy1 * t)
            self.intersection = [intersection_x, intersection_y]

            logger.info(f"Found intersection: {self.intersection}")

            return intersection_x, intersection_y
        else:
            logger.info(f"No intersection found.")
            return []
        
    def detect(self,img):
        """
        @description: 检测函数入口
        """
        self.img = img.copy()

        self.preprocess_image()

        vertices       = self.find_max_quad_vertices()
        scale_vertices = self.find_scale_quad_vertices()
        intersection   = self.calculate_intersection()
        points_list    = self.segment_line()

        return vertices, scale_vertices, intersection
    
    def draw(self, img=None):
        """
        @description: 绘制检测结果
        """
        if img is None:
            img = self.img.copy()
        def draw_point_text(img, x, y, bgr = ( 0, 0, 255)): #绘制一个点，并显示其坐标。
            cv2.circle(img, (x, y), 5, bgr, -1)
            cv2.putText(
                img,
                f"({x}, {y})",
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 1, cv2.LINE_AA,
            )
            return img

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
        
        def draw_segment_points(img, points_list):
            logger.debug(f"Found points list: {points_list}")
            for points_num in points_list:
                for point in points_num:
                    cv2.circle(img, (int(point[0]), int(point[1])), 3, (0, 255, 255), -1)
            
            return img

        img_drawed = draw_lines_points(self.img, self.vertices)          # 绘制最大四边形
        img_drawed = draw_lines_points(img_drawed, self.scale_vertices)  # 绘制缩放四边形
        img_drawed = draw_segment_points(img_drawed, self.points_list)   # 绘制等分点
        img_drawed = draw_point_text(img_drawed, self.intersection[0], self.intersection[1]) # 绘制交点

        return img_drawed


class PointDetector:
    def __init__(self, roi_vertices=None):
        """
        @param roi_vertices: ROI 区域的四个顶点坐标
        """
        self.img = None
        self.roi_vertices = roi_vertices

        self.red_point   = None
        self.green_point = None

    def roi_cut(self, img, roi_vertices):
        """
        @description: ROI 区域裁剪
        @param img: 输入图像
        @param roi_vertices: ROI 区域的四个顶点坐标
        @return: 裁剪后的图像
        """
        roi_vertices = np.array(roi_vertices, dtype=np.int32)
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, [roi_vertices], (255, 255, 255))
        masked_image = cv2.bitwise_and(img, mask)

        return masked_image

    @staticmethod
    def find_point(image):
        """
        @description: 寻找红点绿点的坐标
        @param image: 输入图像
        @return: 红点坐标, 绿点坐标
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        def find_max_contours(mask):
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) > 0:
                # 找到最大的轮廓
                largest_contour = max(contours, key=cv2.contourArea)
                # 找到最大轮廓的外接矩形
                x, y, w, h = cv2.boundingRect(largest_contour)  
                
                center_x = int(x + w / 2)  # 计算中心点 x 坐标
                center_y = int(y + h / 2)  # 计算中心点 y 坐标

                point = [x, y, w, h, center_x, center_y]
                # print(point)
                return point
            else:
                return [0,0,0,0,0,0]
            
        def find_red_point(hsv):
            # 红色范围
            lower = np.array([0, 100, 100])
            upper = np.array([10, 255, 255])
            mask1 = cv2.inRange(hsv, lower, upper)

            lower = np.array([160, 100, 100])
            upper = np.array([179, 255, 255])
            mask2 = cv2.inRange(hsv, lower, upper)

            mask = mask1 | mask2

            return find_max_contours(mask)
        def find_green_point(hsv):
            # 绿色范围
            lower = np.array([40, 100, 100])
            upper = np.array([80, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)

            return find_max_contours(mask)
        
        def find_yellow_point(hsv):
            # 黄色范围
            lower = np.array([26, 43, 46])
            upper = np.array([34, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            return find_max_contours(mask)
        
        def find_white_point(hsv):
            # 白色范围
            lower = np.array([0, 0, 200])
            upper = np.array([180, 30, 255])
            mask = cv2.inRange(hsv, lower, upper)
            return find_max_contours(mask)

        red_point = find_red_point(hsv)
        green_point = find_green_point(hsv)

        # 特殊情况处理
        if red_point[0] == 0 and green_point[0] == 0:
            yellow_point = find_yellow_point(hsv)
            red_point    = yellow_point
            green_point  = yellow_point
            logger.info("红绿光重叠, 找黄光")

            if yellow_point[0] == 0:
                white_point = find_white_point(hsv)
                red_point   = white_point
                green_point = white_point
                logger.info("黄光找不到, 找白光")

        logger.info(f"red_point: {red_point[4], red_point[5]} | green_point: {green_point[4], green_point[5]}")

        return red_point, green_point
    
    def detect(self, img, roi=[]):
        """
        @param img: 待检测图像
        @param roi: ROI 区域, 为空时不裁剪 
        """

        if len(roi) > 0:
            self.img = self.roi_cut(img.copy(), roi)
            # cv2.imshow("roi", self.img)
        else:
            self.img = img.copy()

        self.red_point, self.green_point = self.find_point(self.img)
        
        return self.red_point, self.green_point
    
    def draw(self, img=None):
        """
        @param img: 待绘制图像, 为空时使用内部图像
        """
        if img is None:
            img = self.img.copy()
        def draw_point(img, point, bgr = ( 0, 255, 255) , color = ' '):
            [x, y, w, h, center_x, center_y] = point
            # 在图像上绘制方框
            cv2.rectangle(img, (x, y), (x + w, y + h), bgr, 1)

            # 绘制坐标
            text = f"{color} point: ({center_x}, {center_y})"
            cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, bgr, 1)

            return img
        
        img_drawed = draw_point(img,   self.red_point,   (0, 255, 255),   "red")
        img_drawed = draw_point(img_drawed, self.green_point, (0, 255, 255), "green")

        return img_drawed

if __name__ == '__main__':

    print("开始测试")
    
    img = cv2.imread("img/rgb.jpg")
    
    quad_detector = QuadDetector(21000, 100, 500/600)
    vertices, scale_vertices, intersection = quad_detector.detect(img)
    img_ = quad_detector.draw()

    point_detector = PointDetector()
    red_point, green_point = point_detector.detect(img,vertices)
    img_ = point_detector.draw(img_)

    cv2.imshow("img_src", img)
    cv2.imshow("img_detected", img_)
    cv2.waitKey(0)