import pygame

button_mapping = {
    "A": 0,
    "B": 1,
    "X": 2,
    "Y": 3,
    "L": 4,
    "R": 5,
    "BACK": 6,
    "START": 7,
    "HOME": 8,
    "LCLICK": 9,
    "RCLICK": 10
}
def init_joysticks():
    """
    初始化所有连接的摇杆控制器。
    
    返回:
    - joysticks: 初始化后的摇杆列表。
    """
    pygame.init()  # 初始化Pygame库
    joysticks = [
        pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())
    ]  # 创建摇杆对象列表
    for joystick in joysticks:
        joystick.init()  # 初始化每个摇杆
    return joysticks

def get_button_input(joystick):
    """
    获取指定摇杆的按钮输入状态。
    
    参数:
    - joystick: pygame.joystick.Joystick对象, 指定的摇杆。
    
    返回:
    - 按钮输入状态列表, 列表中每个元素代表对应按钮的状态 (0为未按下, 非0为按下 )。
    - 对应按钮顺序可能是 [A, B, X, Y, L, R, BACK, START, HOME, LCLICK, RCLICK]
    """
    return [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

def get_hat_input(joystick):
    """
    获取指定摇杆的帽形开关输入状态。
    
    参数:
    - joystick: pygame.joystick.Joystick对象, 指定的摇杆。
    
    返回:
    - 帽形开关输入状态列表, 每个帽形开关以元组形式表示其方向 (如(-1, -1)表示左下角 )。
    """
    return [joystick.get_hat(i) for i in range(joystick.get_numhats())]

def get_axis_input(joystick):
    """
    获取指定摇杆的轴输入状态。
    
    参数:
    - joystick: pygame.joystick.Joystick对象, 指定的摇杆。
    
    返回:
    - 轴输入状态列表, 列表中每个元素代表对应轴的当前位置 (范围通常在-1到1之间 )。
    - 对应按轴顺序可能是 [LX, LY, ZL, RX, RY, ZR]
    """
    return [joystick.get_axis(i) for i in range(joystick.get_numaxes())]

def close_joysticks(joysticks):
    """
    关闭所有打开的摇杆控制器并退出Pygame库。
    
    参数:
    - joysticks: 需要关闭的摇杆列表。
    """
    for joystick in joysticks:
        joystick.quit()  # 关闭每个摇杆
    pygame.quit()  # 退出Pygame库