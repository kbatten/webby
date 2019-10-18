import io

import PIL

from http.server import BaseHTTPRequestHandler, HTTPServer


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
