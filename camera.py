import pygame as pg
from matrix_operations import *
from copy import copy

class Camera:
    def __init__(self, render, position):
        self.render = render
        self.position = np.array([*position, 1.0])
        self.position_backup = np.array([*position, 1.0])
        self.forward = np.array([0, 0, 1, 1])
        self.up = np.array([0, 1, 0, 1])
        self.right = np.array([1, 0, 0, 1])
        self.h_fov = math.pi / 3
        self.v_fov = self.h_fov * (render.HEIGHT / render.WIDTH)
        self.near_plane = 0.1
        self.far_plane = 100
        self.moving_speed = 0.05
        self.rotation_speed = 0.025

        # For info box
        self.text_color = pg.Color('aqua')
        self.font = pg.font.SysFont("Source Code Pro", 14)
        self.text_position = (20, 20) # (x, y)


    def control(self):
        key = pg.key.get_pressed()
        if key[pg.K_a]:
            self.position -= self.right * self.moving_speed
        if key[pg.K_d]:
            self.position += self.right * self.moving_speed
        if key[pg.K_w]:
            self.position += self.forward * self.moving_speed
        if key[pg.K_s]:
            self.position -= self.forward * self.moving_speed
        if key[pg.K_q]:
            self.position += self.up * self.moving_speed
        if key[pg.K_e]:
            self.position -= self.up * self.moving_speed
        
        if key[pg.K_LEFT]:
            self.camera_yaw(-self.rotation_speed)
        if key[pg.K_RIGHT]:
            self.camera_yaw(self.rotation_speed)
        
        if key[pg.K_UP]:
            self.camera_pitch(self.rotation_speed)
        if key[pg.K_DOWN]:
            self.camera_pitch(-self.rotation_speed)

        # Reset camera position on key C
        if key[pg.K_r]:
            self.position = copy(self.position_backup)
            self.forward = np.array([0, 0, 1, 1])
            self.up = np.array([0, 1, 0, 1])
            self.right = np.array([1, 0, 0, 1])
    

    def draw_info(self):
        cursor_x, cursor_y = self.text_position

        cam_position = self.render.camera.position
        cam_forward = self.render.camera.forward
        cam_up = self.render.camera.up
        cam_right = self.render.camera.right
        cam_position_text = "Coordinates: [{:+5.3f} {:+5.3f} {:+5.3f}]".format(cam_position[0], cam_position[1], cam_position[2])
        cam_forward_text =  "Up:          [{:+5.3f} {:+5.3f} {:+5.3f}]".format(cam_forward[0], cam_forward[1], cam_forward[2])
        cam_up_text =       "Forward:     [{:+5.3f} {:+5.3f} {:+5.3f}]".format(cam_up[0], cam_up[1], cam_up[2])
        cam_right_text =    "Right:       [{:+5.3f} {:+5.3f} {:+5.3f}]".format(cam_right[0], cam_right[1], cam_right[2])

        panel_rows = [
            # (text string,                    px linespace )
            ("Cam control:"                             ,  0),
            ("W / S                   - In /  Out"      , 20),
            ("A / D                   - Left / Right"   , 20),
            ("Q / E                   - Up / Down"      , 20),
            ("Key Up / Key Down       - Pitch"          , 20),
            ("Key Left / Key Right    - Yaw"            , 20),
            ("R                       - Home Camera"    , 20),
            ("Cam position:"                            , 40),
            (cam_position_text                          , 20),
            (cam_forward_text                           , 20),
            (cam_up_text                                , 20),
            (cam_right_text                             , 20),
        ]

        for row in panel_rows:
            cursor_y += row[1]
            tmp_surface = self.font.render(row[0], True, self.text_color, None)
            self.render.screen.blit(tmp_surface, (cursor_x, cursor_y))


    def draw(self):
        self.draw_info()

    def camera_yaw(self, angle):
        rotate = rotate_y(angle)
        self.forward = self.forward @ rotate
        self.right = self.right @ rotate
        self.up = self.up @ rotate


    def camera_pitch(self, angle):
        rotate = rotate_x(angle)
        self.forward = self.forward @ rotate
        self.right = self.right @ rotate
        self.up = self.up @ rotate


    def translate_matrix(self):
        x, y, z, w = self.position
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [-x, -y, -z, 1],
        ])


    def rotate_matrix(self):
        rx, ry, rz, w = self.right
        fx, fy, fz, w = self.forward
        ux, uy, uz, w = self.up
        return np.array([
            [rx, ux, fx, 0],
            [ry, uy, fy, 0],
            [rz, uz, fz, 0],
            [0, 0, 0, 1]
        ])


    def camera_matrix(self):
        return self.translate_matrix() @ self.rotate_matrix()
