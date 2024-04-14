import cv2 as cv
import numpy as np

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
    # 转换颜色空间为HSV
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    #降低曝光度
    hsv[:, :, 2] = hsv[:, :, 2] * 1

    rgb = cv.cvtColor(image, cv.COLOR_HSV2BGR)
    cv.imshow('Result', rgb)
    cv.waitKey(0)
    cv.destroyAllWindows()


    if color == 'red':
        # 红色范围
        lower = np.array([0, 100, 100])
        upper = np.array([10, 255, 255])
        mask1 = cv.inRange(hsv, lower, upper)

        lower = np.array([160, 100, 100])
        upper = np.array([179, 255, 255])
        mask2 = cv.inRange(hsv, lower, upper)

        # 合并红色范围的掩码
        mask = mask1 + mask2
    elif color == 'green':
        # 绿色范围
        lower = np.array([40, 100, 100])
        upper = np.array([80, 255, 255])
        mask = cv.inRange(hsv, lower, upper)
    else:
        return None

    # 找到轮廓
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        # 找到最大的轮廓
        largest_contour = max(contours, key=cv.contourArea)
        # 找到最大轮廓的外接矩形
        x, y, w, h = cv.boundingRect(largest_contour)

        # 在图像上绘制方框
        cv.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # 绘制坐标
        text = f"{color} point: ({x}, {y})"
        cv.putText(image, text, (x + w + 10, y + int(h / 2)), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    return [color,x,y]

def main():
    image = cv.imread("img/red.png")

    # 查找最大的红点
    rimg = find_largest_blob(image, 'red')

    print(rimg)

    # 查找最大的绿点
    #find_largest_blob(image, 'green')

    # 显示结果图像
    cv.imshow('Result', image)
    cv.imwrite("rag-out.jpg", image)
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == '__main__':                                                                                                          
    main()