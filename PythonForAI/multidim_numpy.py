import numpy as np
class datamatrics_class(object):
    def __init__(self, data):
        self.data = data
    def get_shape(self):
        return self.data.shape
    def get_size(self):
        return self.data.size
    def get_ndim(self):
        return self.data.ndim
    def get_dtype(self):
        return self.data.dtype
    




