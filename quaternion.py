import numpy as np
import math
class Quaternion():
    
    def __init__(self, r, i, j, k):
        mag = math.sqrt((r * r) + (i * i) + (j * j) + (k * k))
        self.r = r / mag
        self.i = i / mag
        self.j = j / mag
        self.k = k / mag

    def times(self, q2):
        return Quaternion (
            (self.r * q2.r) - (self.i * q2.i) - (self.j * q2.j) - (self.k * q2.k),
            (self.r * q2.i) + (self.i * q2.r) + (self.j * q2.k) - (self.k * q2.j),
            (self.r * q2.j) + (self.j * q2.r) + (self.k * q2.i) - (self.i * q2.k),
            (self.r * q2.k) + (self.k * q2.r) + (self.i * q2.j) - (self.j * q2.i),
        )
    def inverse(self):
        return Quaternion (self.r, -self.i, -self.j, -self.k)