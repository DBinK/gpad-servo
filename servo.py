import subprocess

# 将旋转角度(-90, +90)映射到(1500±1000) for servo
def angle_to_high_time(angle):
    
    normalized_angle  = (angle + 90) / 180      # 将(-90, +90)范围映射到0到1之间
    high_time = int(normalized_angle  * 2000 + 500)  # 将0到1的值映射到1500±1000之间
    
    return high_time

# 将手柄输入(-1,1)映射到(-90,90) for gpad
def gpad_to_angle(gpad_input):
    if gpad_input == -3.0517578125e-05:
        return 0
    else:
        return gpad_input * 90

# gpio pwmt [wpipin] [high_time] [period_time] 
# gpio pwmt 3 2500 20000 
# 旋转指令
def rt(wpipin, angle):
    wpipin = str(wpipin)
    high_time = str(angle_to_high_time(angle))
    print(f"gpio pwmt {wpipin} {high_time} 20000")
    subprocess.call(['gpio', 'pwmt', wpipin, high_time, '20000'])

