import jsonpickle
import numpy as np
import math

class VL53L5CX_Target:
    signal_per_spad: int | None
    range_sigma_mm: int | None
    distance_mm: int | None
    reflectance: int | None
    target_status: int | None

    def __init__(
        self, 
        signal_per_spad: int, 
        range_sigma_mm: int, 
        distance_mm: int,
        reflectance: int,
        target_status: int
        ):
        self.signal_per_spad = signal_per_spad
        self.range_sigma_mm = range_sigma_mm
        self.distance_mm = distance_mm
        self.reflectance = reflectance
        self.target_status = target_status


class VL53L5CX_Zone:
    ambient_per_spad: int | None
    nb_target_detected: int | None
    nb_spads_enabled: int | None
    target: VL53L5CX_Target | None

    def __init__(
        self, 
        ambient_per_spad: int, 
        nb_target_detected: int, 
        nb_spads_enabled: int,
        target: VL53L5CX_Target
        ):
        self.ambient_per_spad = ambient_per_spad
        self.nb_target_detected = nb_target_detected
        self.nb_spads_enabled = nb_spads_enabled
        self.target = target


class VL53L5CX_Reading:
    nb_zones: int
    silicon_temp_degc: int | None
    zones: list[VL53L5CX_Zone] | None

    def __init__(self, data: str):
        # print(data)
        nb_zones = int(data[0])
        if nb_zones not in [16, 64]:
            raise ValueError

        self.nb_zones = nb_zones
        self.row_len = int(math.sqrt(nb_zones))    # 4 or 8 depending on incoming data
        self.silicon_temp_degc = int(data[1])
        temp_list_of_zones = list()
        # print(f'data len: {len(data)}')

        for i in range(0, self.nb_zones):
            # Calculate index/offset per zone
            z_index = 2 + (i * 8)

            temp_ambient_per_spad = int(data[z_index + 0])
            temp_nb_target_detected = int(data[z_index + 1])
            temp_nb_spads_enabled = int(data[z_index + 2])

            temp_target = VL53L5CX_Target(
                signal_per_spad=int(data[z_index + 3]),
                range_sigma_mm=int(data[z_index + 4]),
                distance_mm=int(data[z_index + 5]),
                reflectance=int(data[z_index + 6]),
                target_status=int(data[z_index + 7])
            )

            zone = VL53L5CX_Zone(
                ambient_per_spad=temp_ambient_per_spad,
                nb_target_detected=temp_nb_target_detected,
                nb_spads_enabled=temp_nb_spads_enabled,
                target=temp_target
            )
            temp_list_of_zones.append(zone)
            
        self.zones = temp_list_of_zones

    def get_distance_matrix(self):
        return np.asmatrix(
            np.array(
                [[self.zones[r * self.row_len + c].target.distance_mm for c in range(self.row_len)] for r in range(self.row_len)]
            )
        )
    
    def get_zone_matrix(self):
        return np.array(
            [[self.zones[r * self.row_len + c] for c in range(self.row_len)] for r in range(self.row_len)]
        )

    def print_temp(self):
        print(f'Silicon temperature: {self.silicon_temp_degc} degrees celcius')

    def rotate_ccw(self):
        rotated_zone_list = [None] * self.nb_zones
        for ix, zone in enumerate(self.zones):
            y_s1 = int(ix / self.row_len)
            x_s1 = ix % self.row_len

            y_s2 = (self.row_len - 1) - x_s1
            x_s2 = y_s1

            rotated_zone_list[x_s2 + (y_s2 * self.row_len)] = zone
        
        # Overwrite with rotated
        self.zones = rotated_zone_list

    def get_point_cloud(self):
        # Not implemented for 4x4 resolution
        if self.nb_zones != 64:
            return None
        
        # Only 8x8 resolution
        points = np.empty([0, 4])
        for ix, zone in enumerate(self.zones):
            theta_x = get_theta_x(ix % 8)
            theta_y = get_theta_y(ix // 8)
            hypothenuse = zone.target.distance_mm / 1000
            points = np.concatenate((points, calc_3d_point(hypothenuse, theta_x, theta_y)), axis=0)

        return points

# Math

"""Calculates and returns coordinates for point in 3d space"""
def calc_3d_point(h: np.float64, theta_x: np.float64, theta_y: np.float64):
    f_y = h * math.sin(theta_y)
    adj_y = h * math.cos(theta_y)
    f_x = adj_y * math.sin(theta_x)
    f_z = adj_y * math.cos(theta_x)

    return np.array([(f_y, f_x, f_z, 1)], dtype=np.float64)

"""Index 0 is 'leftmost' zone, -7/64 pi, incremented 2/64 for each zone in x direction"""
def get_theta_x(x: int):
    return ((-7 + (x * 2)) / 64) * math.pi

"""Index 0 is top row of zone, 7/64 pi, decremented 2/64 for each row (positive y direction)"""
def get_theta_y(y: int):
    return ((7 - (y * 2)) / 64) * math.pi

# File
def save_readings_json(readings: list[VL53L5CX_Reading], path: str):
    f = open(path, 'w')
    json_obj = jsonpickle.encode(readings)
    f.write(json_obj)
    f.close()

def read_json_file(path: str):
    f = open(path)
    return jsonpickle.decode(f.read())