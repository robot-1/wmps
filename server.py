from distutils.log import debug
import os
from posixpath import dirname

import tornado.ioloop
from tornado.options import define, options, parse_command_line
import tornado.web
import tornado.autoreload

import socketio

define('port', default=5000, help="run on the given port", type=int)
define('debug', default=False, help='run in debug mode')

sio = socketio.AsyncServer(async_mode='tornado', cors_allowed_origins=['http://localhost:5000'])

@sio.on('my response')
async def client_response(sid, data):
    dtype = data['type']
    if dtype == 'ping':
        await sio.emit('ping_from_server', {'data': data['ping']['latency']}, room='/dashboard')
    elif dtype == 'download':
        await sio.emit('dl_result', {'data': data['download']['bandwidth']}, room='/dashboard')
    elif dtype == 'upload':
        await sio.emit('ul_result', {'data': data['upload']['bandwidth']}, room='/dashboard')

@sio.event
async def start_speedtest(sid):
    await sio.emit('speedtest_task', {'data': 'hello'})
    

@sio.event
async def connect(sid, environ, auth):
    print('Connect', sid)
    await sio.emit('my_response', {'data': 'Please Join Room'}, room=sid)
    #tornado.ioloop.IOLoop.current().spawn_callback(background_task)
    #tornado.ioloop.IOLoop.current().spawn_callback(background_task)

@sio.event
async def join_dashboard(sid):
    print('joining...')
    sio.enter_room(sid, '/dashboard')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

def addwatchfiles(*paths):
    for p in paths:
        file_path = os.path.abspath(p)
        print(file_path)
        tornado.autoreload.watch(file_path)

if __name__ == "__main__":
    parse_command_line()
    app = tornado.web.Application([
        (r'/', MainHandler),
        (r'/socket.io/', socketio.get_tornado_handler(sio)),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug,
    )
    app.listen(options.port)
    tornado.autoreload.start()
    addwatchfiles('templates/index.html')
    tornado.ioloop.IOLoop.current().start()

