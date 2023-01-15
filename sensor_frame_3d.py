from object_3d import Object3D, any_func
import numpy as np
import pygame as pg
from copy import copy
from VL53L5CX import calc_3d_point, get_theta_x, get_theta_y, VL53L5CX_Reading

COLOR_FIRST_TARGET  = pg.Color('magenta')
COLOR_SECOND_TARGET = pg.Color('aqua')
COLOR_THIRD_TARGET  = pg.Color('greenyellow')
COLOR_FOURTH_TARGET  = pg.Color('lightcoral')

COLOR_SELECT = [
    COLOR_FIRST_TARGET,
    COLOR_SECOND_TARGET,
    COLOR_THIRD_TARGET,
    COLOR_FOURTH_TARGET,
]

# Max targets: 
# VL53L5CX can detect up to 4 targets per zone.
# 64 * 4 = 256
MAX_TARGETS = 256

# TARGET STATUS: (From UM2884 rev 3)
# 0     Ranging data are not updated
# 1     Signal rate too low on SPAD array
# 2     Target phase
# 3     Sigma estimator too high
# 4     Target consistency failed
# 5     Range valid
# 6     Wrap around not performed (typically the first range)
# 7     Rate consistency failed
# 8     Signal rate too low for the current range
# 9     Range valid with large pulse (may be due to a merged target)
# 10    Range valid, but no target detected at previous range
# 11    Target blurred by another one, due to sharpener
# 12    Target detected, but inconsistent data. Frequently happens for secondary targets
# 255   No target detected (only if number of target detected is enabled)
VALID_TARGET_STATUS = [5, 9, 10]

class Sensor3D(Object3D):
    def __init__(self, render, color):
        super().__init__(render)
        
        self.vertices = np.zeros((MAX_TARGETS, 4))
        self.vertices_enabled = True

        # Allocate for variations in drawing color, size, etc.
        self.vertex_color = [COLOR_FIRST_TARGET] * MAX_TARGETS
        self.target_draw_size = [0] * MAX_TARGETS
        
        # Filter - Are conditions for drawing this point fulfilled?
        self.target_draw_filter = [False] * MAX_TARGETS

    
    def update_pointcloud(self, sensor_frame: VL53L5CX_Reading):
        # Only 8x8 resolution
        if sensor_frame.nb_zones != 64:
            # TODO: Implement support for 4*4 configurations
            return None
        
        
        points = np.empty([0, 4])
        draw_cond_fulfilled = [True] * MAX_TARGETS
        self.target_draw_size = [0] * MAX_TARGETS
        for ix_z, zone in enumerate(sensor_frame.zones):

            # Get thetas for zone position
            theta_x = get_theta_x(ix_z % 8)
            theta_y = get_theta_y(ix_z // 8)

            for ix_t, target in enumerate(zone.targets):
                hypothenuse = target.distance_mm / 1000
                points = np.concatenate((points, calc_3d_point(hypothenuse, theta_x, theta_y)), axis=0)

                # calculate ix of resulting target (point/vertex + filter)
                target_arr_ix = (ix_z * sensor_frame.nb_targets_per_zone) + ix_t

                # Select color for vertex
                self.vertex_color[target_arr_ix] = COLOR_SELECT[ix_t]

                # Apply filter "Target status"
                if target.target_status not in VALID_TARGET_STATUS:
                    draw_cond_fulfilled[target_arr_ix] = False

                # Apply other filters below...
                distance = float(target.distance_mm / 1000)
                if distance < 0.2:
                    self.target_draw_size[target_arr_ix] = 10
                elif distance < 0.5:
                    self.target_draw_size[target_arr_ix] = 9
                elif distance < 0.7:
                    self.target_draw_size[target_arr_ix] = 8
                elif distance < 1.0:
                    self.target_draw_size[target_arr_ix] = 7
                elif distance < 1.70:
                    self.target_draw_size[target_arr_ix] = 6
                else:
                    draw_cond_fulfilled[target_arr_ix] = False
                    self.target_draw_size[target_arr_ix] = 1

        
        self.vertices = points
        self.target_draw_filter = draw_cond_fulfilled


    def draw(self):
        super().screen_projection()


    def draw_vertices(self, vertices):
        for ix, vertex in enumerate(vertices):
            if self.target_draw_filter[ix]:
                if not any_func(vertex, self.render.H_WIDTH, self.render.H_HEIGHT):
                    pg.draw.circle(self.render.screen, self.vertex_color[ix], vertex, self.target_draw_size[ix])
