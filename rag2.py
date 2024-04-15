import cv2 
import numpy as np

def roi_cut(image, vertices):
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [vertices], (255, 255, 255))
    masked_image = cv2.bitwise_and(image, mask)

    return masked_image
def find_largest_blob(image, color):
    """
    查找图像中最大的特定颜色的Blob（区域）。

    参数:
    - image: 输入的图像，使用BGR颜色空间。
    - color: 指定要查找的颜色，字符串类型，支持'red'和'green'。

    返回值:
    - 如果找到最大的Blob，则返回一个列表，包含颜色、Blob的x和y坐标。
    - 如果没有找到指定颜色的Blob，则返回None。
    """
    #image = cv2.GaussianBlur(image, (15, 15), 0)
    #cv2.imshow("image", image)

    # 转换颜色空间为HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    if color == 'red':
        # 红色范围
        lower = np.array([0, 100, 100])
        upper = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower, upper)

        lower = np.array([160, 100, 100])
        upper = np.array([179, 255, 255])
        mask2 = cv2.inRange(hsv, lower, upper)

        # 合并红色范围的掩码
        mask = mask1 | mask2
    elif color == 'green':
        # 绿色范围
        lower = np.array([40, 100, 100])
        upper = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
    else:
        return None

    # 找到轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        # 找到最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)
        # 找到最大轮廓的外接矩形
        x, y, w, h = cv2.boundingRect(largest_contour)

        # 在图像上绘制方框
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # 绘制坐标
        text = f"{color} point: ({x}, {y})"
        cv2.putText(image, text, (x + w + 10, y + int(h / 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        return image, [x, y]
    else:
        return [0,[0,0]]
    

def find_point(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    def find_max_contours(mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            # 找到最大的轮廓
            largest_contour = max(contours, key=cv2.contourArea)
            # 找到最大轮廓的外接矩形
            x, y, w, h = cv2.boundingRect(largest_contour)
            point = [x, y, w, h]
            return point
    def find_red_point(hsv):
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

    red_point = find_red_point(hsv)
    green_point = find_green_point(hsv)
    
    return red_point, green_point
def draw_point(image, point):

    [x, y, w, h] = point
    # 在图像上绘制方框
    cv2.rectangle(image, (x, y), (x + w, y + h), ( 0, 255, 255), 1)

    # 绘制坐标
    text = f"red point: ({x}, {y})"
    cv2.putText(image, text, (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    return image

if __name__ == '__main__':                                                                                                          


    try:    
        image = cv2.imread("img/rgb.jpg")
        vertices = np.array([[150, 28], [179, 533], [625, 481], [610, 36]])
        #image = roi_cut(image, vertices)
        

        """ cv2.imshow('Result', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows() """

        # 查找最大的红点
        rimg = find_largest_blob(image, 'red')

        print(rimg)

        # 查找最大的绿点
        find_largest_blob(image, 'green')

        # 显示结果图像
        cv2.imshow('Result', image)
        cv2.imwrite("rag-out.jpg", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    except Exception as e:
        print(e)