
import gpad

import pygame
from time import sleep

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
        print("Button input:", button_input)
        print("Hat input:", hat_input)
        print("Axis input:", axis_input)

gpad.close_joysticks(joysticks)