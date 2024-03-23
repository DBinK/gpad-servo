import subprocess

# gpio pwmt [wpipin] [high_time] [period_time] 
# gpio pwmt 3 2500 20000 

def angle_to_high_time(angle):
    
    high_time = (angle + 90) / 180  # 将(-90, +90)范围映射到0到1之间
    high_time = high_time * 1000 + 500         # 将0到1的值映射到1500±1000之间
    
    return high_time

def rt(wpipin, angle):
    high_time = 2000/180 
    subprocess.call(['gpio', 'pwmt', wpipin, high_time, '20000'])

