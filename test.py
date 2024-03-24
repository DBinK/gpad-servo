import pygame
import gpad

from time import sleep

""" print(servo.angle_to_high_time(9))

print(servo.rt(3, 90)) """

sampling = 0.1  

joysticks = gpad.init_joysticks()

running = True
paused = False  # 添加一个变量来跟踪是否暂停

while running:

    sleep(sampling)  
    
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
        print(f"按钮输入: {button_input}")

    # 键值表
    # [A, B, X, Y, L, R, BACK, START, HOME, LCLICK, RCLICK]
    # [0, 1, 2, 3, 4, 5,    6,     7,    8,      9,     10]

    if button_input[7] == 1:
        if paused:
            paused = False  # 再次按下START，继续循环
            print("继续")
        else:
            paused = True  # 按下右键，暂停循环
            print("暂停")
            
    if button_input[10] == 1:
        running = False
        print("退出程序")

    # 如果暂停，跳过当前循环的执行
    if paused:
        continue

# 游戏结束或退出时，关闭所有游戏手柄连接
gpad.close_joysticks(joysticks)