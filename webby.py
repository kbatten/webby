#!/usr/bin/env python3

import sys
import math

from mathics.world import World
from mathics.viewport import Viewport
from mathics.machines.basic import Machine, Point

from gifserve import write_gif, serve_gif


class Web(Machine):
    range_radii = (26, 35)
    range_anchor_points = (3, 9)
    range_hub_position_disturbance = (-1.5, 1.5)
    range_spiral_distance_factor = (0.03, 0.04)
    range_spiral_disturbance = (0, 0.02)

    def __init__(self):
        super(Web, self).__init__()
        self.center = Point(50, 50)

    def visualization(self, vp):
        Viewport = vp

        vp.add_object(Viewport.Text(Point(3,3), self.dyn_t, (170,130,170)))

        # select center
        vp.add_object(Viewport.Circle(self.center, self.dyn_select_center_point_rad, Viewport.WHITE))

    def dyn_t(self):
        return "%0.2f s" % self.t

    def dyn_select_center_point(self):
        return Point(50 + 10*math.sin(2*self.t), 50 + 10*math.cos(2*self.t))

    def dyn_select_center_point_rad(self):
        ret = 4.0
        if self.t < 0.5:
            t = 2.0 * self.t
            ret = 1.0 + ret * self.ease_in_out_sin(t)
        elif self.t < 1:
            t = 2.0 * self.t - 1.0
            ret = 1.0 + ret - self.ease_in_out_sin(t)
        return ret

    @staticmethod
    def ease_in_out_sin(t):
        return 0.5 + 0.5 * math.sin(t * math.pi - math.pi / 2.0)


def setup_world(w, h, supersample):
    # create world
    world = World(w, h, font=("/usr/share/fonts/truetype/lato/Lato-Bold.ttf", 16), supersample=supersample)

    # create one viewport that is entire world
    viewport = Viewport(0, 0, 99, 99)
    world.add_viewport(viewport, 0, 0, w-1, h-1)

    # add Web machine
    web = Web()
    world.add_machine(web)
    viewport.add_visualization(web.visualization)

    return world


def main():
    WIDTH = 500
    HEIGHT = 500
    SUPERSAMPLE = 2
    TIME_DURATION = 5
    SECONDS_PER_FRAME = 0.05

    TIME_START_SEC = 0
    TIME_DURATION_SEC = SECONDS_PER_FRAME * math.ceil(TIME_DURATION / SECONDS_PER_FRAME)

    world = setup_world(WIDTH, HEIGHT, SUPERSAMPLE)
    frames = world.get_frames(TIME_START_SEC, TIME_DURATION_SEC, SECONDS_PER_FRAME)

    gif = write_gif(frames, TIME_DURATION_SEC)

    print("starting server")
    serve_gif(gif)



if __name__ == "__main__":
    sys.exit(main())
