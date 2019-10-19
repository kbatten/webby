#!/usr/bin/env python3

import sys
import math
import time
import random

from contextlib import contextmanager

from mathics.world import World
from mathics.viewport import Viewport
from mathics.machines.basic import Machine, Point

from video import write_webp, write_webm, serve_webm



class Web(Machine):
    range_radii = (26, 35)
    range_anchor_points = (3, 9)
    range_hub_position_disturbance = (-1.5, 1.5)
    range_spiral_distance_factor = (0.03, 0.04)
    range_spiral_disturbance = (0, 0.02)

    def __init__(self):
        super(Web, self).__init__()

    def orientation(self, a, b, c):
        x1 = a[0]
        y1 = a[1]
        x2 = b[0]
        y2 = b[1]
        x3 = c[0]
        y3 = c[1]

        o = (y2-y1) * (x3-x2) - (y3-y2)*(x2-x1)
        if o < 0:
            return -1
        if o > 0:
            return 1
        return 0

    def intersection(self, p1, q1, p2, q2):
        return self.orientation(p1, q1, p2) != self.orientation(p1, q1, q2) and self.orientation(p2, q2, p1) != self.orientation(p2, q2, q1)

    def cast_ray(self, origin, angle, dist):
        # for now our walls are the edges of the canvas
        x = origin.x + dist * math.sin(angle)
        y = origin.y + dist * math.cos(angle)

        # http://www.dcs.gla.ac.uk/~pat/52233/slides/Geometry1x1.pdf
        # two vectors intersect if
        #  p = wall
        #  q = ray
        #  1. (p1,q1,p2) and (p1,q1,q2) have different orientations
        #     (p2,q2,p1) and (p2,q2,q1) have different orientations

        p2 = (origin.x, origin.y)
        q2 = (x, y)

        # check top
        p1 = (0, 0)
        q1 = (99, 0)
        if self.intersection(p1, q1, p2, q2):
            return Point(x, y), True
        # check bottom
        p1 = (0, 99)
        q1 = (99, 99)
        if self.intersection(p1, q1, p2, q2):
            return Point(x, y), True
        # check left
        p1 = (0, 0)
        q1 = (0, 99)
        if self.intersection(p1, q1, p2, q2):
            return Point(x, y), True
        # check right
        p1 = (99, 0)
        q1 = (99, 99)
        if self.intersection(p1, q1, p2, q2):
            return Point(x, y), True

        return Point(x, y), False

    def visualization(self, vp):
        vp.add_object(Viewport.Text(Point(3,3), self.dyn_t, (170,130,170)))

        # select a center
        center_x_perturb = random.random() * 15
        center_y_perturb = random.random() * 15
        center = Point(50+center_x_perturb, 50+center_y_perturb)
        vp.add_object(Viewport.Circle(center, self.dyn_select_center_point_rad, Viewport.WHITE))

        # cast rays at ~30 degrees from center
        angle_offset = (math.pi * 2.0) / self.range_anchor_points[1]
        for i in range(9):
            angle_perturb = random.random() * angle_offset / 2.0
            ray, attached = self.cast_ray(center, i*angle_offset+angle_perturb, 60)
            if attached:
                vp.add_object(Viewport.Line(center, ray, 1, (192, 192, 192)))
            else:
                vp.add_object(Viewport.Line(center, ray, 1, (192, 0, 0)))

    def dyn_t(self):
        return "%0.2f s" % self.t

    def dyn_select_center_point(self):
        return Point(50 + 10*math.sin(2*self.t), 50 + 10*math.cos(2*self.t))

    def dyn_select_center_point_rad(self):
        scale = 0.25  # t=0 -> 0.5
        ret = 3.0
        if self.t < scale:
            t = self.t / scale
            ret = 1.0 + ret * self.ease_in_out_sin(t)
        elif self.t < scale * 2.0:
            t = self.t / scale - 1.0
            ret = 1.0 + ret - self.ease_in_out_sin(t)
        return ret

    def dyn_attach_point_1(self):
        return self.dyn_attach_point_1_3(self.attach_point_1)

    def dyn_attach_point_2(self):
        return self.dyn_attach_point_1_3(self.attach_point_2)

    def dyn_attach_point_3(self):
        return self.dyn_attach_point_1_3(self.attach_point_3)

    def dyn_attach_point_1_3(self, attach_point):
        start = 0.5
        scale = 0.5 # t=0.5 -> 1.0
        ret = Point(self.center.x + attach_point.x, self.center.y + attach_point.y)
        if self.t < start:
            ret = self.center
        elif self.t < start + scale:
            t = (self.t - start) / scale
            x = self.center.x + attach_point.x * self.ease_in_out_sin(t)
            y = self.center.y + attach_point.y * self.ease_in_out_sin(t)
            ret = Point(x, y)
        return ret

    def dyn_attach_point_1_color(self):
        return self.dyn_attach_point_1_3_color(self.attach_point_1)

    def dyn_attach_point_2_color(self):
        return self.dyn_attach_point_1_3_color(self.attach_point_2)

    def dyn_attach_point_3_color(self):
        return self.dyn_attach_point_1_3_color(self.attach_point_3)

    def dyn_attach_point_1_3_color(self, attach_point):
        end_point = self.dyn_attach_point_1_3(attach_point)
        x_2 = (end_point.x-self.center.x)*(end_point.x-self.center.x)
        y_2 = (end_point.y-self.center.y)*(end_point.y-self.center.y)
        dist = math.sqrt(x_2 + y_2)
        if dist > 55:
            return (192, 0, 0)
        return (192, 192, 192)


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



@contextmanager
def timit(message, args=None):
    start_time = time.time()
    try:
        yield(start_time)
    finally:
        end_time = time.time()
        if args:
            print(message.format(end_time - start_time, *args))
        else:
            print(message.format(end_time - start_time))



def main():
    WIDTH = 500
    HEIGHT = 500
    SUPERSAMPLE = 2
    TIME_DURATION = 2
    SECONDS_PER_FRAME = 0.0333
    DEMO_SECONDS_PER_FRAME = 0.1

    TIME_START_SEC = 0
    TIME_DURATION_SEC = SECONDS_PER_FRAME * math.ceil(TIME_DURATION / SECONDS_PER_FRAME)

    world = setup_world(WIDTH, HEIGHT, SUPERSAMPLE)

    timit_args = []
    with timit("webm get_frames {1} frames in {0:.1f} seconds", timit_args):
        frames = world.get_frames(TIME_START_SEC, TIME_DURATION_SEC, SECONDS_PER_FRAME)
        timit_args.append(len(frames))

    with timit("webm write_webm {0:.1f} seconds"):
        video = write_webm(frames, TIME_DURATION_SEC, WIDTH, HEIGHT)

    timit_args = []
    with timit("webp get_frames {1} frames in {0:.1f} seconds", timit_args):
        frames = world.get_frames(TIME_START_SEC, TIME_DURATION_SEC, DEMO_SECONDS_PER_FRAME)
        timit_args.append(len(frames))

    with timit("webp write_webp {0:.1f} seconds"):
        demo = write_webp(frames, TIME_DURATION_SEC)

    with open("demo.webp", "wb") as f:
        demo.seek(0)
        f.write(demo.read())

    print("starting server")
    serve_webm(video)



if __name__ == "__main__":
    sys.exit(main())
