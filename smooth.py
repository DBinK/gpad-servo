class SmoothFilter:
    """
    平滑滤波器类，用于通过滑动窗口的方式对数据进行平滑处理。
    
    参数:
    window_size -- 滑动窗口的大小，决定了平滑程度。
    """
    def __init__(self, window_size):
        """
        初始化函数，创建一个滑动窗口，并初始化存储值的列表。
        
        参数:
        window_size -- 滑动窗口的大小。
        """
        self.window_size = window_size
        self.values = []  # 用于存储窗口内数值的列表
    
    def update(self, value):
        """
        更新函数，将新值加入到滑动窗口中，并在窗口大小超出时移除最旧的值。
        
        参数:
        value -- 需要加入滑动窗口的新值。
        """
        self.values.append(value)  # 将新值添加到窗口的尾部
        if len(self.values) > self.window_size:  # 如果窗口大小超出，则移除最旧的值
            self.values.pop(0)
    
    def get_smooth_value(self):
        """
        获取平滑后的值，通过计算窗口内所有值的平均数实现。
        
        返回:
        平滑后的值。如果窗口内没有值，则返回0。
        """
        return sum(self.values) / len(self.values) if self.values else 0  # 计算平均数，如果没有值则返回0