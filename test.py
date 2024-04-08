from PIL import Image, ImageDraw

def shrink_rectangle(x1, y1, x2, y2, x3, y3, x4, y4, center_x, center_y):
    """
    已知四边形四个顶点坐标和中心点坐标,计算缩小 0.5 倍后的四边形坐标
    """
    # 计算缩小后的四个顶点坐标
    new_x1 = center_x + (x1 - center_x) * 0.5
    new_y1 = center_y + (y1 - center_y) * 0.5
    new_x2 = center_x + (x2 - center_x) * 0.5
    new_y2 = center_y + (y2 - center_y) * 0.5
    new_x3 = center_x + (x3 - center_x) * 0.5
    new_y3 = center_y + (y3 - center_y) * 0.5
    new_x4 = center_x + (x4 - center_x) * 0.5
    new_y4 = center_y + (y4 - center_y) * 0.5

    return new_x1, new_y1, new_x2, new_y2, new_x3, new_y3, new_x4, new_y4

# 示例使用
x1, y1 = 0, 0
x2, y2 = 1, 4
x3, y3 = 3, 4
x4, y4 = 2, 0
center_x, center_y = 2, 2

new_x1, new_y1, new_x2, new_y2, new_x3, new_y3, new_x4, new_y4 = shrink_rectangle(x1, y1, x2, y2, x3, y3, x4, y4, center_x, center_y)

# 创建一个 400x400 像素的图像
img = Image.new("RGB", (400, 400), (255, 255, 255))
draw = ImageDraw.Draw(img)

# 绘制原始四边形
draw.polygon([(x1 * 100, y1 * 100), (x2 * 100, y2 * 100), (x3 * 100, y3 * 100), (x4 * 100, y4 * 100)], outline=(0, 0, 0))

# 绘制缩小后的四边形
draw.polygon([(new_x1 * 100, new_y1 * 100), (new_x2 * 100, new_y2 * 100), (new_x3 * 100, new_y3 * 100), (new_x4 * 100, new_y4 * 100)], outline=(255, 0, 0))

# 保存图像
img.save("output.png")
