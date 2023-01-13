from object_3d import *
from camera import *
from projection import *
import pygame as pg
from workers import ReplayWorker, SerialPortWorker
from surface_3d import CheckerBoard
from command_args import run_arg_parse

"""
Commands:
    -h  --help          Help

    -l  --live          Open program with connection to sensor live via serial port
                        Parameters:
    -p                  Serial port e.g. 'COM3' or '/dev/TTY*' [String] (MANDATORY)
    -o                  Output file path [String]                       (OPTIONAL)

    -rp --replay        Open program and and get input from file.
                        Parameters:
    -i                  Input file path [String]                        (MANDATORY)
    -f                  Playback frequency [Int, Hz]                    (OPTIONAL)
"""

class Window3D:
    def __init__(self):        
        args = run_arg_parse()
        pg.init()
        self.RES = self.WIDTH, self.HEIGHT = 1920, 1080
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT //2
        self.FPS = 60
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.create_objects()
        self.workers = list()

        if args.replay:
            self.workers.append(
                ReplayWorker(
                    render=self,
                    path_to_file=args.i,
                    frequency=args.f,
                    point_color=pg.Color('magenta')
                )
            )

        elif args.live:
            self.workers.append(
                SerialPortWorker(
                    render=self,
                    com_port=args.p,
                    baud_rate=args.b,
                    path_to_save=args.o,
                    point_color=pg.Color('magenta')
                )
            )

        else:
            pass

        for worker in self.workers:
            worker.start()


    def create_objects(self):
        self.camera = Camera(self, [0.5, 1, -7] )
        self.projection = Projection(self)

        # Set up a "room" to make it easier to percieve depth while viewing sensor output
        self.floor = CheckerBoard(self, (2.0, 1.5), (0.1, 0.1), pg.Color('gray25'))
        self.floor.rotate_x(math.pi/2)
        self.floor.translate((-1.0, -0.5, 0.0))

        self.rear_wall = CheckerBoard(self, (2.0, 1.5), (0.1, 0.1), pg.Color('gray25'))
        self.rear_wall.translate((-1.0, -0.5, 1.6))


    def draw(self):
        self.screen.fill(pg.Color('gray8'))

        # Draw static objects
        self.floor.draw()
        self.rear_wall.draw()

        # Draw foreground
        for worker in self.workers:
            worker.draw()
        
        self.camera.draw()  # Has info box, draw it.


    def quit(self):
        for worker in self.workers:
            worker.kill()
            worker.join() # the worker in the afterlife
        exit()


    def run(self):
        while True:
            # Event loop
            events = pg.event.get()
            for worker in self.workers:
                worker.control(events)

            for event in events:
                if event.type == pg.QUIT:
                    self.quit()

            # Screen
            self.draw()
            self.camera.control()
            pg.display.set_caption("RemoteViewer")
            pg.display.flip()

            # Tick
            self.clock.tick(self.FPS)


if __name__ == '__main__':
    app = Window3D()
    app.run()
