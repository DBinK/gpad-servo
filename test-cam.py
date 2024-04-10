import cv2
from cam8 import preprocess_image, find_max_perimeter_contour, find_contour_xy, calculate_intersection , draw_contour_and_vertices, draw_max_cnt_rectangle

if __name__ == "__main__":
    img = cv2.imread("img/w2.jpg")
    contours = preprocess_image(img)
    max_perimeter, max_cnt = find_max_perimeter_contour(contours)

    if max_cnt is not None:
        vertices = find_contour_xy(max_cnt, max_perimeter)
        fin_img, intersection = draw_contour_and_vertices(img, vertices)
        fin_img = draw_max_cnt_rectangle(fin_img, vertices)

    if vertices is not None:
        intersection = calculate_intersection(vertices)
        print(f"交点的坐标: ({intersection[0]}, {intersection[1]})")
        print(f"四个顶点坐标: \n {vertices}")

    # 显示的图像
    
    cv2.imshow("final", fin_img)
    cv2.imwrite("out/x-out.jpg", fin_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows() 



