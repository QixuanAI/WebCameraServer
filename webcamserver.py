#! /usr/bin/env python
'''
Description : Build a web camera server quickly.
Author      : qxairobot@163.com
Date        : 2021-06-30
Refer to    : https://github.com/QixuanAI/WebCameraServer
'''

from __future__ import print_function, absolute_import
import sys
import cv2
import base64
import numpy as np
from PIL import Image
from tornado import web, httpserver, ioloop, websocket

JPEG_HEADER = "data:image/jpeg;base64,"
INDEX = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>display</title>
</head>
<body>
    <canvas id="canvas"></canvas>
</body>

<script type="text/javascript">
var url=window.location.host;
url=url.substring(url.lastIndexOf('/')+1,url.length);
var ws=new WebSocket("ws://"+url+"/video");
var canvas=document.getElementById("canvas");
var timer=setInterval(function(){
	if(ws.readyState==1){
		ws.send("msg");
		clearInterval(timer);
		}
	},10);
ws.onmessage=function(res){
	var img_src=JSON.parse(res.data)["img"];
	var img=new Image();
	img.src=img_src;
	img.onload=function(){
		var ctx=canvas.getContext("2d");
		canvas.setAttribute("width",img.width);
		canvas.setAttribute("height",img.height);
		ctx.drawImage(img,0,0);
		ws.send("msg");
	}
}
</script>
</html>
"""

cap = cv2.VideoCapture(0)
assert cap.isOpened(), "can't open camera!"


def get_image_dataurl():
    _, frame = cap.read()
    _, buf = cv2.imencode(".jpeg", frame)
    dat = Image.fromarray(np.uint8(buf)).tobytes()
    img_date_url = JPEG_HEADER + str(base64.b64encode(dat))[2:-1]
    return img_date_url


class IndexHandler(web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write(INDEX)


class VideoHandler(websocket.WebSocketHandler):
    def on_message(self, message):
        self.write_message({"img": get_image_dataurl()})


if __name__ == '__main__':
    if sys.argv[1:]:
        url = sys.argv[1]
        if (':' in url):
            address = url.split(':')[0]
            port = int(url.split(':')[1])
        else:
            address = '0.0.0.0'
            port = int(url)
    else:
        port = 22637
        address = '0.0.0.0'

    app = web.Application(handlers=[
        (r"/", IndexHandler),
        (r"/index", IndexHandler),
        (r'/video', VideoHandler)
    ])
    http_server = httpserver.HTTPServer(app)
    http_server.listen(port=port, address=address)
    print("WebCamera Server URL: http://{}:{}/index".format(address, port))
    ioloop.IOLoop.instance().start()
