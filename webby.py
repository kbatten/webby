#!/usr/bin/env python3

import sys

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

    def visualization(self, vp, data={}):
        Viewport = vp
        vp.add_object(Viewport.Circle(Point(50, 50), 5, Viewport.WHITE))


def setup_world(w, h, supersample):
    # create world
    world = World(w, h, supersample=supersample)

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

    world = setup_world(WIDTH, HEIGHT, SUPERSAMPLE)

    TIME_START_SEC = 0
    TIME_DURATION_SEC = 5
    SECONDS_PER_FRAME = 0.05
    frames = world.get_frames(TIME_START_SEC, TIME_DURATION_SEC, SECONDS_PER_FRAME)

    gif = write_gif(frames, TIME_DURATION_SEC)
    serve_gif(gif)



if __name__ == "__main__":
    sys.exit(main())
