import cv2
import numpy as np
import sys
from loguru import logger

# 设置日志级别为 DEBUG
logger.remove()
logger.add(sys.stderr, level="DEBUG")  # 输出到stderr（默认是控制台），级别为DEBUG

class PointDetector:
    def __init__(self, img):
        self.img = img.copy()
        