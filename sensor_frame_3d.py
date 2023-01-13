from object_3d import Object3D
import numpy as np
from copy import copy

class Sensor3D(Object3D):
    def __init__(self, render, color):
        super().__init__(render)
        
        self.vertices = np.zeros((64, 4))
        self.draw_vertices = True
        self.vertex_color = color
        self.vertex_size = 6

    def update_point_cloud(self, point_cloud):
        # Shallow copy, avoid referencing
        self.vertices = np.array(copy(point_cloud))


    def draw(self):
        super().draw()