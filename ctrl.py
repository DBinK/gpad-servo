import board,busio,time
from adafruit_pca9685 import PCA9685

# Create the I2C bus interface.
#i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = busio.I2C(board.GP1, board.GP0)    # Pi Pico RP2040
i2c = busio.I2C(board.SCL1, board.SDA1)

# Create a simple PCA9685 class instance.
pca = PCA9685(i2c)

# Set the PWM frequency to 60hz.
pca.frequency = 50

# Set the PWM duty cycle for channel zero to 50%. duty_cycle is 16 bits to match other PWM objects
# but the PCA9685 will only actually give 12 bits of resolution.

while 1:
    for i in range(1200,18000,10):
        ht = int(i / 20000 * 0xFFFF)
        print(ht)
        pca.channels[0].duty_cycle = int(ht)
        pca.channels[3].duty_cycle = int(ht)
        time.sleep(0.02)
    
    time.sleep(1)
    
    for i in range(18000,1200,-10):
        ht = int(i / 20000 * 0xFFFF)
        print(ht)
        pca.channels[0].duty_cycle = int(ht)
        pca.channels[3].duty_cycle = int(ht)
        time.sleep(0.02)
    
    time.sleep(1)

    for i in range(18000,1200,-10):
        ht = int(i / 20000 * 0xFFFF)
        print(ht)
        pca.channels[4].duty_cycle = int(ht)
        pca.channels[7].duty_cycle = int(ht)
        time.sleep(0.02)
    
    time.sleep(1)