import pygame as pg
import numpy as np
from matrix_operations import *
from numba import njit


@njit(fastmath=True)
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))

class Object3D:
    def __init__(self, render):
        self.render = render
        self.vertices = np.empty([0, 4], dtype=np.float64)

        self.faces = np.array([
        ], dtype=np.int32)

        self.font = pg.font.SysFont('Arial', 30, bold=True)
        self.color_faces = [(pg.Color('orange'), face) for face in self.faces]
        self.draw_vertices, self.draw_faces, self.draw_labels = False, False, False
        self.label = ''
        self.vertex_color = pg.Color('white')
        self.vertex_size = 3
        self.edge_color = None

    def draw(self):
        self.screen_projection()


    def screen_projection(self):
        vertices = self.vertices @ self.render.camera.camera_matrix()
        vertices = vertices @self.render.projection.projection_matrix
        vertices /= vertices[:, -1].reshape(-1, 1)
        vertices[(vertices > 1) | (vertices < -1)] = 0
        vertices = vertices @ self.render.projection.to_screen_matrix
        vertices = vertices[:, :2]

        if self.draw_faces:
            for index, color_face in enumerate(self.color_faces):
                color, face = color_face
                polygon = vertices[face]
                if not any_func(polygon, self.render.H_WIDTH, self.render.H_HEIGHT):
                    try:
                        pg.draw.polygon(self.render.screen, color, polygon, width=0)
                    except(TypeError):
                        pass
                        # print(polygon)
                    if self.label and self.draw_labels:
                        text = self.font.render(self.label[index], True, pg.Color('white'))
                        self.render.screen.blit(text, polygon[-1])

        if self.draw_vertices:
            for vertex in vertices:
                if not any_func(vertex, self.render.H_WIDTH, self.render.H_HEIGHT):
                    pg.draw.circle(self.render.screen, self.vertex_color, vertex, self.vertex_size)
        

    def translate(self, pos):
        self.vertices = self.vertices @ translate(pos)


    def scale(self, scale_to):
        self.vertices = self.vertices @ scale(scale_to)


    def rotate_x(self, angle):
        self.vertices = self.vertices @ rotate_x(angle)


    def rotate_y(self, angle):
        self.vertices = self.vertices @ rotate_y(angle)


    def rotate_z(self, angle):
        self.vertices = self.vertices @ rotate_z(angle)