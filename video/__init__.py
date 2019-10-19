import io

from http.server import BaseHTTPRequestHandler, HTTPServer

from tempfile import NamedTemporaryFile

import PIL
import cv2
import numpy



def write_gif(frames, duration):
    video = io.BytesIO()
    for i in range(len(frames)):
        frames[i] = frames[i].convert('P', palette = PIL.Image.ADAPTIVE)
    frames[0].save(video, format="GIF", save_all=True, append_images=frames[1:], duration=duration/len(frames), loop=0)
    return video

def write_webp(frames, duration):
    video = io.BytesIO()
    frames[0].save(video, format="webp", save_all=True, append_images=frames[1:], duration=int(duration/len(frames)), loop=0)
    return video

def write_webm(frames, duration, width, height):
    fps = len(frames)/duration
    video = io.BytesIO()
    fourcc = cv2.VideoWriter_fourcc(*'VP90')
    api_preference = cv2.CAP_ANY

    with NamedTemporaryFile(suffix=".webm") as f:
        filename = f.name

        out = cv2.VideoWriter(filename, api_preference, fourcc=fourcc, fps=fps, frameSize=(width, height))
        for frame in frames:
            cv_frame = numpy.array(frame)
            cv_frame = cv2.cvtColor(cv_frame, cv2.COLOR_RGB2BGR)
            out.write(cv_frame)

        out.release()

        with open(filename, "rb") as f:
            video.write(f.read())

    return video

def serve_gif(video):
    serve_video(video, "image/gif")

def serve_webp(video):
    serve_video(video, "image/webp")

def serve_webm(video):
    serve_video(video, "video/webm")

def serve_video(video, content_type):
    PORT_NUMBER = 8000

    class myHandler(BaseHTTPRequestHandler):
        #Handler for the GET requests
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type',content_type)
            self.end_headers()

            video.seek(0)
            self.wfile.write(video.read())
            return

    try:
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
