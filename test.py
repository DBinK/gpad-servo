def average_points(point1, point2, N=2):
    """
    根据两个给定点和分段数N, 计算这两个点之间等分的坐标点列表。
    """
    delta_x = (point2[0] - point1[0]) / N
    delta_y = (point2[1] - point1[1]) / N

    points_list = []

    for i in range(N + 1):
        x = point1[0] + delta_x * i
        y = point1[1] + delta_y * i
        points_list.append([x, y])

    return points_list


def draw_line_points(image, small_vertices):
    for i, j in [0, 1], [1, 2], [2, 3], [3, 0]:
        points_list = average_points(small_vertices[i], small_vertices[j], 4)
        for point in points_list:
            x, y = point
            cv2.circle(image, (int(x), int(y)), 2, (0, 0, 255), -1)
            """ print(int(x),int(y))
        print("----------") """


if __name__ == "__main__":

    small_vertices = [[11, 21], [122, 12], [123, 213], [14, 214]]

    draw_line_points(None, small_vertices)
