import subprocess

def angle_to_high_time(angle):
    """
    将旋转角度(-90, +90)映射到(1500±1000)的脉冲宽度时间 for servo

    参数:
    angle: float, 表示旋转角度，范围为-90到+90度。

    返回值:
    int, 映射后的脉冲宽度时间，范围为1500±1000。
    """
    normalized_angle  = (angle + 90) / 180           # 将角度范围(-90, +90)标准化到0到1之间
    high_time = int(normalized_angle  * 2000 + 500)  # 将标准化的角度映射到1500±1000的范围内，并转换为整数
    
    return high_time

def gpad_to_angle(gpad_input, min_angle, max_angle):
    """
    将GPAD（通用位置角度描述）输入转换为指定范围内的角度值。

    参数:
    gpad_input - GPAD输入值，预期为一个介于0和1之间的数值，代表角度范围的相对位置。
    min_angle - 角度范围的最小值（单位：度）。
    max_angle - 角度范围的最大值（单位：度）。

    返回值:
    计算得到的角度值（单位：度），位于[min_angle, max_angle]范围内。
    """
    
    angle_range = max_angle - min_angle     # 计算角度范围
    angle = gpad_input * angle_range / 2 + (max_angle + min_angle) / 2   # 根据GPAD输入值计算角度
    return angle

# gpio pwmt [wpipin] [high_time] [period_time] 
# gpio pwmt 3 2500 20000 
def rt(wpipin, angle):
    """
    实现旋转指令的功能。
    
    参数:
    - wpipin: 用于旋转的GPIO引脚编号，整数类型。
    - angle: 旋转的角度，整数或浮点数类型。
    """
    # 将输入的wpipin和计算出的high_time转换为字符串类型，以备后续命令行调用
    wpipin = str(wpipin)
    high_time = str(angle_to_high_time(angle))
    
    # 打印并执行旋转指令
    print(f"gpio pwmt {wpipin} {high_time} 20000")
    subprocess.call(['gpio', 'pwmt', wpipin, high_time, '20000'])

