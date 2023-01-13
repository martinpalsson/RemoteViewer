
from sensor_frame_3d import Sensor3D
import pygame as pg
from VL53L5CX import read_json_file, save_readings_json, VL53L5CX_Reading
import threading
import serial
from datetime import datetime
import pygame as pg


class ReplayWorker(threading.Thread):
    def __init__(self, render, path_to_file: str, frequency: int, point_color: pg.Color):
        threading.Thread.__init__(self)

        self.killed = False
        self.clock = pg.time.Clock()

        self.sensor = Sensor3D(render, point_color)
        self.update_frequency = frequency
        self.frames = read_json_file(path_to_file)

        self.ix = 0
        self.ix_max = len(self.frames)
        self.replay_state = "Paused"
        self.replay_dir = "Forward"

        # For infobox:
        self.info_position = (20, 300)
        self.bg_color = pg.Color('magenta')
        self.text_color = pg.Color('aqua')
        self.font = pg.font.SysFont("Source Code Pro", 14)

        self.next_frame()
        
    def draw(self):
        self.sensor.draw()
        self.draw_info()

    def kill(self):
        self.killed = True

    def update(self):
        if self.replay_state == "Playing":
            if self.replay_dir == "Forward":
                self.next_frame()
            else:
                self.previous_frame()

    # To be called by main event loop
    def control(self, events):
        for event in events:
            if event.type == pg.KEYDOWN:
                key = event.key
                if key == pg.K_SPACE:
                    if self.replay_state == "Paused":
                        self.replay_state = "Playing"
                    else:
                        self.replay_state = "Paused"
                
                if key == pg.K_x:
                    if self.replay_dir == "Forward":
                        self.replay_dir = "Reverse"
                    else:
                        self.replay_dir = "Forward"
                
                if key == pg.K_z:
                    self.previous_frame()

                if key == pg.K_c:
                    self.next_frame()
    
    def draw_info(self):
        cursor_x, cursor_y = self.info_position
        panel_rows = [
            # (text string,                    px linespace )
            ("Replay control:"                          ,  0),
            ("Space                   - Pause/Play"     , 20),
            ("X                       - Toggle reverse" , 20),
            ("Z                       - Previous frame" , 20),
            ("C                       - Next frame"     , 20),
            ("Key Left / Key Right    - Yaw"            , 20),
            (f'Frame #                 - {self.ix}'     , 40),
            (f'Replay direction        - {self.replay_dir}', 20),
            (f'Replay state            - {self.replay_state}', 20),
        ]

        for row in panel_rows:
            cursor_y += row[1]
            tmp_surface = self.font.render(row[0], True, self.text_color, None)
            self.sensor.render.screen.blit(tmp_surface, (cursor_x, cursor_y))

    def next_frame(self):
        self.ix += 1
        
        if self.ix >= self.ix_max:
            self.ix = 0 # Replay from 0

        self.sensor.vertices = self.frames[self.ix].get_point_cloud()
    
    def previous_frame(self):
        self.ix -= 1

        if self.ix < 0:
            self.ix = self.ix_max - 1
        
        self.sensor.vertices = self.frames[self.ix].get_point_cloud()
    
    def run(self):
        try:
            while not self.killed:
                self.update()
                self.clock.tick(self.update_frequency)
        finally:
            pass # Just die


class SerialPortWorker(threading.Thread):
    def __init__(self, render, com_port: str, baud_rate: int, path_to_save: str | None, point_color: pg.Color):
        threading.Thread.__init__(self)

        self.killed = False
        self.clock = pg.time.Clock()

        self.sensor = Sensor3D(render, point_color)
        # Filename, default is log_<datetime>.json
        if path_to_save == "":
            file_timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
            self.path_to_save = f'log_{file_timestamp}.json'
        else:
            self.path_to_save = path_to_save
        
        # Read frames are stored in self.frames. Can be saved when worker is killed.
        self.frames = list()

        # Start serial communication.
        self.serial = serial.Serial(com_port, baud_rate, timeout=1)
        self.serial.flush()

        # Need to put at least some data in the frame
        # wait for something on serial and poll before exiting __init__
        # while not self.serial.in_waiting:
        #     sleep(0.1)
        self.poll()


    def draw(self):
        self.sensor.draw()


    def kill(self):
        save_readings_json(self.frames, self.path_to_save)
        self.killed = True


    def poll(self):
        try:
            if self.serial.in_waiting:
                rx_data = self.serial.read_until()
                data_chunks = rx_data.decode().replace(" ", "").strip().split(';')
                reading = VL53L5CX_Reading(data_chunks)
                
                self.sensor.vertices = reading.get_point_cloud()
                self.frames.append(reading)
        except(ValueError):
            pass
    
    def control(self, events):
        # No functions to control as of now
        pass

    def run(self):
        while not self.killed:
            self.poll()
            self.clock.tick(60)