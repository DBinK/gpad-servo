import board
import busio
import time
from adafruit_pca9685 import PCA9685

class ServoController:
    def __init__(self):
        """
        初始化ServoController类。
        """
        self.i2c = busio.I2C(board.SCL2, board.SDA2)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50  # 将 PWM 频率设置为 50Hz

    @staticmethod
    def angle_process(angle: float) :
        """
        将角度转换为 PCA9685 的 duty_cycle 值。
        """

        high_time = angle / 180 * 2000 + 500
        duty_cycle = high_time / 20000 * 0xFFFF
        return int(duty_cycle), high_time

    def rotate_angle(self, channel: int, angle: float, limit = [0 ,360]):
        """
        控制指定通道旋转到特定角度。
        """
        if angle <= limit[0]: 
            angle = limit[0]
        if angle >= limit[1]:
            angle = limit[1]
                
        self.pca.channels[channel].duty_cycle, _ = self.angle_process(angle)

    def led(self, channel: int, brightness: int):
        """
        控制指定通道的亮度。
        """
        self.pca.channels[channel].duty_cycle = int(brightness / 100 * 0xFFFF)

    def release(self):
        """
        停止PCA9685输出信号并释放资源。
        """
        self.pca.deinit()

    def restore(self):
        """
        恢复对PCA9685的控制。
        """
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50  # 恢复 PWM 频率设置为 50Hz

    def reset(self):
        for i in range(0,15):
            self.rotate_angle(i, 90)


    def test_servo(self, max_angle=1350, min_angle=450, step=5, speed=0.01):
        """
        测试函数，用于测试舵机的旋转。
        """
        while True:
            for i in range(min_angle, max_angle, step):
                self.rotate_angle(0, i / 10)
                self.rotate_angle(3, i / 10)
                print(i)
                time.sleep(speed)

            time.sleep(1)

            for i in range(max_angle, min_angle, -step):
                self.rotate_angle(0, i / 10)
                self.rotate_angle(3, i / 10)
                print(i)
                time.sleep(speed)

            time.sleep(1)
    
    def test_led(self, max_brightness=100, min_brightness=0, step=5, speed=0.01):
        """
        测试函数, 用于测试LED的亮度。
        """
        while True:
            for i in range(min_brightness, max_brightness, step):
                self.led(15, i)
                print(i)
                time.sleep(speed)
            time.sleep(1)
            for i in range(max_brightness, min_brightness, -step):
                self.led(15, i)
                print(i)
                time.sleep(speed)
            time.sleep(1)

            self.led(15, 0)
            time.sleep(0.5)
            self.led(15, 100)
            time.sleep(0.5)
            self.led(15, 0)
            time.sleep(0.5)
            self.led(15, 100)
            time.sleep(0.5)
            self.led(15, 0)
            time.sleep(0.5)
            self.led(15, 100)
            time.sleep(0.5)
            self.led(15, 0)
            time.sleep(0.5)
            self.led(15, 100)
            time.sleep(0.5)
            self.led(15, 0)
            time.sleep(0.5)
            self.led(15, 100)
            time.sleep(0.5)
            self.led(15, 0)
            time.sleep(0.5)
            self.led(15, 100)
            time.sleep(0.5)
            

if __name__ == '__main__':
    controller = ServoController()
    #controller.test_led()
    controller.test_servo()
