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
    targets: list[VL53L5CX_Target] | None

    def __init__(
        self, 
        ambient_per_spad: int, 
        nb_target_detected: int, 
        nb_spads_enabled: int,
        targets: list[VL53L5CX_Target] | None,
        ):
        self.ambient_per_spad = ambient_per_spad
        self.nb_target_detected = nb_target_detected
        self.nb_spads_enabled = nb_spads_enabled
        self.targets = targets


class VL53L5CX_Reading:
    nb_zones: int
    nb_targets_per_zone: int
    silicon_temp_degc: int | None
    zones: list[VL53L5CX_Zone] | None

    def __init__(self, data: list[str]):
        # Read tokenized data in string format
        ix = 0 # index..
        nb_zones = int(data[0]) # a.k.a resolution
        self.nb_targets_per_zone = int(data[ix:=ix+1])
        self.silicon_temp_degc = int(data[ix:=ix+1])

        if nb_zones not in [16, 64]:
            raise ValueError

        self.nb_zones = nb_zones
        self.row_len = int(math.sqrt(nb_zones))    # 4 or 8 depending on incoming data
        temp_list_of_zones = list()
        
        for _ in range(0, self.nb_zones):
            # Using pre-increments on z_index
            temp_ambient_per_spad = int(data[ix:=ix+1])
            temp_nb_target_detected = int(data[ix:=ix+1])
            temp_nb_spads_enabled = int(data[ix:=ix+1])

            targets = list()
            for _ in range(self.nb_targets_per_zone):

                temp_target = VL53L5CX_Target(
                    signal_per_spad=int(data[ix:=ix+1]),
                    range_sigma_mm=int(data[ix:=ix+1]),
                    distance_mm=int(data[ix:=ix+1]),
                    reflectance=int(data[ix:=ix+1]),
                    target_status=int(data[ix:=ix+1])
                )
                targets.append(temp_target)

            zone = VL53L5CX_Zone(
                ambient_per_spad=temp_ambient_per_spad,
                nb_target_detected=temp_nb_target_detected,
                nb_spads_enabled=temp_nb_spads_enabled,
                targets=targets
            )
            temp_list_of_zones.append(zone)
            
        self.zones = temp_list_of_zones

    def print_temp(self):
        print(f'Silicon temperature: {self.silicon_temp_degc} degrees celcius')

    # Note: This is a remainder from old raster rendering of the data frame.
    # Probably cheaper to rotate the 3d object around one of the axis 
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


    # Note: This method is no longer used. Can probably be deleted.
    # Point cloud conversion has been moved to Sensor3D
    """Converts all targets to points in 3d space"""
    def get_point_cloud(self):
        # Not implemented for 4x4 resolution
        if self.nb_zones != 64:
            return None
        
        # Only 8x8 resolution
        points = np.empty([0, 4])
        for ix_z, zone in enumerate(self.zones):
            theta_x = get_theta_x(ix_z % 8)
            theta_y = get_theta_y(ix_z // 8)
            for _, target in enumerate(zone.targets):
                hypothenuse = target.distance_mm / 1000
                points = np.concatenate((points, calc_3d_point(hypothenuse, theta_x, theta_y)), axis=0)

        return points

# TODO: Migrate math to Sensor3D?

"""Calculates and returns coordinates for point in 3d space"""
def calc_3d_point(h: np.float64, theta_x: np.float64, theta_y: np.float64):
    f_y = h * math.sin(theta_y)
    adj_y = h * math.cos(theta_y)
    f_x = adj_y * math.sin(theta_x)
    f_z = adj_y * math.cos(theta_x)

    return np.array([(f_y, f_x, f_z, 1)], dtype=np.float64)

# TODO: Make get_thetas to work with 4*4 resolution
"""Index 0 is 'leftmost' zone, -7/64 pi, incremented 2/64 pi for each zone in x direction"""
def get_theta_x(x: int):
    return ((-7 + (x * 2)) / 64) * math.pi

"""Index 0 is top row of zone, 7/64 pi, decremented 2/64 pi for each row (positive y direction)"""
def get_theta_y(y: int):
    return ((7 - (y * 2)) / 64) * math.pi

# File operations
def save_readings_json(readings: list[VL53L5CX_Reading], path: str):
    f = open(path, 'w')
    json_obj = jsonpickle.encode(readings)
    f.write(json_obj)
    f.close()

def read_json_file(path: str):
    f = open(path)
    return jsonpickle.decode(f.read())