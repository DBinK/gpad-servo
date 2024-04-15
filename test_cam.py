import cv2
import numpy as np

def find_circle(img):
    # Step1. 转换为HSV
    hue_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Step2. 用颜色分割图像 192, 207, 247  rgb(176, 196, 246)
    low_range = np.array([0, 123, 100])
    high_range = np.array([5, 255, 255])
    th = cv2.inRange(hue_image, low_range, high_range)

    # Step3. 形态学运算，膨胀
    dilated = cv2.dilate(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)

    # Step4. Hough Circle
    circles = cv2.HoughCircles(dilated, cv2.HOUGH_GRADIENT, 1, 100, param1=15, param2=7, minRadius=10, maxRadius=20)

    # Step5. 绘制
    if circles is not None:
        x, y, radius = circles[0][0]
        center = (x, y)
        print(center)
        cv2.circle(img, center, radius, (0, 255, 0), 2)

    return img

def find_red_circle(img):
    # 在彩色图像的情况下，解码图像将以b g r顺序存储通道。
    grid_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 从RGB色彩空间转换到HSV色彩空间
    grid_HSV = cv2.cvtColor(grid_RGB, cv2.COLOR_RGB2HSV)

    # H、S、V范围一：
    lower1 = np.array([0,43,46])
    upper1 = np.array([10,255,255])
    mask1 = cv2.inRange(grid_HSV, lower1, upper1)       # mask1 为二值图像
    res1 = cv2.bitwise_and(grid_RGB, grid_RGB, mask=mask1)

    # H、S、V范围二：
    lower2 = np.array([156,43,46])
    upper2 = np.array([180,255,255])
    mask2 = cv2.inRange(grid_HSV, lower2, upper2)
    res2 = cv2.bitwise_and(grid_RGB,grid_RGB, mask=mask2)

    # 将两个二值图像结果 相加
    mask3 = mask1 + mask2

    # Step4. Hough Circle
    circles = cv2.HoughCircles(mask3, cv2.HOUGH_GRADIENT, 1, 100, param1=15, param2=7, minRadius=10, maxRadius=20)

    # Step5. 绘制
    if circles is not None:
        x, y, radius = circles[0][0]
        center = (x, y)
        print(center)
        cv2.circle(img, center, radius, (0, 255, 0), 2)

    return img


if __name__ == '__main__':
    img = cv2.imread('img/rgb.jpg')
    find_red_circle(img)

    cv2.imshow('result', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    
    # 结果显示
    """ cv2.imshow("mask3", mask3)
    cv2.imshow("Mask1",mask1)
    cv2.imshow("res1",res1)
    cv2.imshow("Mask2",mask2)
    cv2.imshow("res2",res2)
    cv2.imshow("grid_RGB", grid_RGB[:,:,::-1])           # imshow()函数传入的变量也要为b g r通道顺序
    cv2.waitKey(0)
    cv2.destroyAllWindows() """
