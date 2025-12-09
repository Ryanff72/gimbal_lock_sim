import numpy as np
from OpenGL.GL import *

def create_ring_vertices(radius, axis='x', segments=64):
    # make taurus
    vertices = []
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        if axis == 'x':
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = 0
        elif axis == 'y':
            x = radius * np.cos(angle)
            y = 0
            z = radius * np.sin(angle)
        elif axis == 'z':
            x = 0
            y = radius * np.cos(angle)
            z = radius * np.sin(angle)

        vertices.append([x, y, z])
    
    return vertices