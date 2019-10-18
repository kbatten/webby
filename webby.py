#!/usr/bin/env python3

import sys
import io

from http.server import BaseHTTPRequestHandler, HTTPServer

import PIL

from mathics.world import World
from mathics.viewport import Viewport
from mathics.machines.basic import Machine, Point



class Web(Machine):
    range_radii = (26, 35)
    range_anchor_points = (3, 9)
    range_hub_position_disturbance = (-1.5, 1.5)
    range_spiral_distance_factor = (0.03, 0.04)
    range_spiral_disturbance = (0, 0.02)

    def __init__(self, width, height):
        super(Web, self).__init__()
        self.width = width
        self.height = height

    def visualization(self, vp, data={}):
        Viewport = vp
        vp.add_object(Viewport.Circle(Point(self.width/2, self.height/2), (self.width+self.height)/20, Viewport.WHITE))


def setup_world(w, h):
    # create world
    world = World(w, h, Viewport.BLACK)

    # create one viewport that is entire world
    viewport = Viewport(0, 0, w-1, h-1)
    world.add_viewport(viewport, 0, 0, w-1, h-1)

    # add Web machine
    web = Web(w, h)
    world.add_machine(web)
    viewport.add_visualization(web.visualization)

    return world


def write_gif(frames, duration):
    gif = io.BytesIO()
    for i in range(len(frames)):
        frames[i] = frames[i].convert('P', palette = PIL.Image.ADAPTIVE)
    frames[0].save(gif, format="GIF", save_all=True, append_images=frames[1:], duration=duration/len(frames), loop=0)
    return gif

def serve_gif(gif):
    PORT_NUMBER = 8000

    class myHandler(BaseHTTPRequestHandler):
        #Handler for the GET requests
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type','image/gif')
            self.end_headers()

            gif.seek(0)
            self.wfile.write(gif.read())
            return

    try:
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()



def main():
    WIDTH = 500
    HEIGHT = 500

    world = setup_world(WIDTH, HEIGHT)

    TIME_START_SEC = 0
    TIME_DURATION_SEC = 5
    SECONDS_PER_FRAME = 0.05
    frames = world.get_frames(TIME_START_SEC, TIME_DURATION_SEC, SECONDS_PER_FRAME)

    gif = write_gif(frames, TIME_DURATION_SEC)
    serve_gif(gif)


if __name__ == "__main__":
    sys.exit(main())
