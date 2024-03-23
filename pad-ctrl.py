import pygame
from time import sleep

# 初始化pygame
pygame.init()

# 获取所有可用的手柄
joysticks = []
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)

# 主循环
running = True
while running:

    #采样间隔控制(单位:秒)
    sleep(0.1)  
    
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 获取手柄输入
    for joystick in joysticks:
        # 获取手柄的轴输入
        for i in range(joystick.get_numaxes()):
            axis_value = joystick.get_axis(i)
            # 打印轴的值
            if axis_value not in [0.0, -1.0, -3.0517578125e-05]:
                print(f"轴 {i} 的值: {axis_value}")
                
        # 获取手柄的帽键按钮
        for i in range(joystick.get_numhats()):
            hat_value = joystick.get_hat(i)
            # 打印按钮的值
            if hat_value != (0,0):
                print(f"按钮 {i} 的值: {hat_value}")
        
        # 获取手柄的按钮输入
        for i in range(joystick.get_numbuttons()):
            button_value = joystick.get_button(i)
            # 打印按钮的值
            if button_value != 0:
                print(f"按钮 {i} 的值: {button_value}")
                
# 退出pygame
pygame.quit()
