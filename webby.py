#!/usr/bin/env python3

import sys

from http.server import BaseHTTPRequestHandler, HTTPServer

import PIL
#from images2gif import writeGif

from mathics.world import World
from mathics.viewport import Viewport



def Web(object):
    range_radii = (26, 35)
    range_anchor_points = (3, 9)
    range_hub_position_disturbance = (-1.5, 1.5)
    range_spiral_distance_factor = (0.03, 0.04)
    range_spiral_disturbance = (0, 0.02)

def setup_world(w, h):
    # create world
    world = World(w, h, Viewport.BLACK)

    # create one viewport that is entire world
    viewport = Viewport(0, 0, w-1, h-1)

    # add Web machine
    web = Web(w, h)
    world.add_machine(web)
    viewport.add_visualization(web.visualization)

    return world

def write_gif(frames, duration):
    gif_name = "image.gif"
    gif = StringIO.StringIO()
    #writeGif(gif, frames, duration/len(frames), nq=0)
    with open(gif_name, "wb") as f:
        gif.seek(0)
        f.write(gif.read())
    return gif_name

def serve_gif(filename):
    PORT_NUMBER = 8000

    with open(gif_name, "rb") as f:
        gif = f.read()

    try:
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

    class myHandler(BaseHTTPRequestHandler):
        #Handler for the GET requests
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type','image/gif')
            self.end_headers()

            gif.seek(0)
            self.wfile.write(gif.read())
            return

def main():
    WIDTH = 500
    HEIGHT = 500

    world = setup_world(WIDTH, HEIGHT)

    TIME_START_SEC = 0
    TIME_DURATION_SEC = 5
    SECONDS_PER_FRAME = 0.05
    frames = world.get_frames(TIME_START_SEC, TIME_DURATION_SEC, SECONDS_PER_FRAME)

    gif_file = write_gif(frames, TIME_DURATION_SEC)
    serve_gif(gif_file)


if __name__ == "__main__":
    sys.exit(main())
