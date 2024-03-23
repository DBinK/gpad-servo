
import gpad
import servo

import pygame
from time import sleep


from smooth_filter import SmoothFilter

Smooth = 1

top_angle_filter = SmoothFilter(window_size = Smooth)  # 创建平滑滤波器对象
button_angle_filter = SmoothFilter(window_size = Smooth)  # 创建平滑滤波器对象

joysticks = gpad.init_joysticks()

running = True
while running:
    sleep(0.1)  # 采样间隔控制(单位:秒)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    for joystick in joysticks:
        button_input = gpad.get_button_input(joystick)
        hat_input = gpad.get_hat_input(joystick)
        axis_input = gpad.get_axis_input(joystick)
        """     
        print("Button input:", button_input)
        print("Hat input:", hat_input) 
        """
        print("Axis input:", axis_input)

        top_angle = servo.gpad_to_angle(axis_input[4])
        top_angle_filter.update(top_angle)  # 更新平滑滤波器
        smoothed_top_angle = top_angle_filter.get_smooth_value()  # 获取平滑后的值
        servo.rt(3, smoothed_top_angle)
        
        button_angle = servo.gpad_to_angle(axis_input[0])
        button_angle_filter.update(-button_angle)  # 更新平滑滤波器
        smoothed_button_angle = button_angle_filter.get_smooth_value()  # 获取平滑后的值
        servo.rt(4, smoothed_button_angle)

gpad.close_joysticks(joysticks)