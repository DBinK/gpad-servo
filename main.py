# 使用Pygame和GPAD模块控制伺服电机，实现游戏手柄对伺服角度的平滑控制
from turtle import speed
import pygame
from time import sleep

# 导入自定义的GPAD、伺服电机控制和平滑滤波器模块
import gpad
import servo
from smooth import SmoothFilter

Smooth = 3  # 设定平滑滤波器的窗口大小
sampling = 0.1  # 控制输入采样间隔，单位为秒，经测试需要不小于0.1秒
mode = 1  # 1为手柄完全跟随模式, 2为手柄步进控制模式, 3为自瞄模式

top_angle    = 0   # 初始化顶部角度
button_angle = 0   # 初始化底部角度
sp           = 1   # 步进速度系数
trubo        = 0.1 # 加速系数

# 初始化两个平滑滤波器，用于处理顶部和按钮的旋转角度输入
top_angle_filter = SmoothFilter(window_size=Smooth)
button_angle_filter = SmoothFilter(window_size=Smooth)

# 初始化游戏手柄
joysticks = gpad.init_joysticks()

# 运行循环，处理游戏手柄输入并控制伺服电机
running = True
while running:

    sleep(sampling)  # 采样间隔
    print(f"\n当前模式: {mode}\n")

    # 处理Pygame事件，如退出事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 遍历连接的游戏手柄，处理输入
    for joystick in joysticks:
        # 获取按钮、方向帽和轴输入
        button_input = gpad.get_button_input(joystick)
        hat_input = gpad.get_hat_input(joystick)
        axis_input = gpad.get_axis_input(joystick)
        print(f"摇杆输入: {axis_input}")
        print(f"帽键输入: {hat_input}")
        print(f"按钮输入: {button_input}\n")

    # 键值表
    # [A, B, X, Y, L, R, BACK, START, HOME, LCLICK, RCLICK]
    # [0, 1, 2, 3, 4, 5,    6,     7,    8,      9,     10]    


    # 完全跟踪模式
    if axis_input[4] is not None and mode == 1:
        # 将轴输入映射并转换为伺服角度，使用平滑滤波器处理后控制伺服电机
        top_angle = servo.gpad_to_angle(axis_input[4], -45, 45)
        top_angle_filter.update(top_angle)  # 注意: 此处对top_angle取正负可控制正反方向
        smoothed_top_angle = top_angle_filter.get_smooth_value()
        print(f"当前角度: {smoothed_top_angle}")
        servo.rt(3, smoothed_top_angle)

    if axis_input[0] is not None and mode == 1:
        button_angle = servo.gpad_to_angle(axis_input[0], -90, 90)
        button_angle_filter.update(-button_angle)  # 注意: 此处对button_angle取正负可控制正反方向
        smoothed_button_angle = button_angle_filter.get_smooth_value()
        print(f"当前角度: {smoothed_button_angle}")
        servo.rt(4, smoothed_button_angle) 
    
    # 步进控制模式 - 摇杆
    if axis_input[4] is not None and mode == 2:
        
        top_speed = servo.gpad_to_angle(axis_input[4], -90, 90)
        top_angle =  top_angle + top_speed*sp
        
        # 限制button_angle在(-90, 90)范围内
        if top_angle < -90:  
            top_angle = -90
        elif top_angle > 90:
            top_angle = 90

        top_angle_filter.update(top_angle)  # 注意: 此处对top_angle取正负可控制正反方向
        smoothed_top_angle = top_angle_filter.get_smooth_value()

        print(f"按钮速度: {top_speed}")
        print(f"当前角度: {smoothed_top_angle}")
        servo.rt(3, smoothed_top_angle)

    if axis_input[0] is not None and mode == 2:
        
        button_speed = servo.gpad_to_angle(axis_input[0], -90, 90)
        button_angle =  button_angle + button_speed*sp

        if button_angle < -90:  # 限制button_angle在(-90, 90)范围内
            button_angle = -90
        elif button_angle > 90:
            button_angle = 90

        button_angle_filter.update(-button_angle)  # 注意: 此处对button_angle取正负翻转控制方向
        smoothed_button_angle = button_angle_filter.get_smooth_value()

        print(f"按钮速度: {button_speed}")
        print(f"当前角度: {smoothed_button_angle}")
        servo.rt(4, smoothed_button_angle)

    # 步进控制模式 - 帽键
    if hat_input[0][0] is not None and mode == 2:
        
        button_speed = servo.gpad_to_angle(hat_input[0][0], -90, 90)
        button_angle =  button_angle + button_speed*trubo

        if button_angle < -90:  # 限制button_angle在(-90, 90)范围内
            button_angle = -90
        elif button_angle > 90:
            button_angle = 90

        button_angle_filter.update(-button_angle)  # 注意: 此处对button_angle取正负翻转控制方向
        smoothed_button_angle = button_angle_filter.get_smooth_value()

        print(f"按钮速度: {button_speed}")
        print(f"当前角度: {smoothed_button_angle}")
        servo.rt(4, smoothed_button_angle)

    if button_input[0]:
        trubo = 1
    else:
        trubo = 0.1

    if button_input[3]:
        if mode == 1:
            mode = 2
            print("\n步进控制模式")
            sleep(0.5) # 消抖，避免重复切换
        elif mode == 2:
            mode = 3
            print("\n自瞄模式")
            sleep(0.5) # 消抖，避免重复切换
        else: 
            mode = 1
            print("\n完全跟踪模式")
            sleep(0.5) # 消抖，避免重复切换

    if button_input[6]:
        running = False
        print("退出程序")


# 游戏结束或退出时，关闭所有游戏手柄连接
gpad.close_joysticks(joysticks)
