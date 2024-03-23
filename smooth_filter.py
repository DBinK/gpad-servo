class SmoothFilter:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []
    
    def update(self, value):
        self.values.append(value)
        if len(self.values) > self.window_size:
            self.values.pop(0)
    
    def get_smooth_value(self):
        return sum(self.values) / len(self.values) if self.values else 0