import pygame
from time import sleep


def init_joysticks():
    pygame.init()
    joysticks = [
        pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())
    ]
    for joystick in joysticks:
        joystick.init()
    return joysticks


def get_button_input(joystick):
    return [joystick.get_button(i) for i in range(joystick.get_numbuttons())]


def get_hat_input(joystick):
    return [joystick.get_hat(i) for i in range(joystick.get_numhats())]


def get_axis_input(joystick):
    return [joystick.get_axis(i) for i in range(joystick.get_numaxes())]


def close_joysticks(joysticks):
    for joystick in joysticks:
        joystick.quit()
    pygame.quit()
