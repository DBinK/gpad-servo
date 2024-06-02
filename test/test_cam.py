
import cv2
import cam


img = cv2.imread('img/tt.jpg')

contours = cam.preprocess_image(img)

# 从输入图像获取4个角点
if contours is not None:
    vertices = cam.find_max_perimeter_contour(contours, 10090*4, 200*4)
    print(vertices)

# 透视变换为矩形，并得到变换矩阵
if vertices is not None:
    M, inv_M = cam.persp_trans(img, vertices)

# 从矩形获取所需坐标
    small_vertices = cam.shrink_rectangle_new(img, (500/600))

    # 获取的坐标乘以矩阵的逆, 得到绝对符合透视的图像
    warped_image, inv_warped_image = cam.draw_warped_image(img, M, inv_M)

    cv2.namedWindow("warped_image", cv2.WINDOW_NORMAL)
    cv2.imshow("warped_image", warped_image)

    cv2.namedWindow("inv_warped_image", cv2.WINDOW_NORMAL)
    cv2.imshow("inv_warped_image", inv_warped_image)

# 显示处理后的图像，并保存
cv2.namedWindow("image", cv2.WINDOW_NORMAL)
cv2.imshow("image", img)



# cv2.imwrite("../out/x-out.jpg", img)
cv2.waitKey(0)
cv2.destroyAllWindows()