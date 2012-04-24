# -*- coding: utf-8 -*-
"""



"""

# tornado
from tornado import websocket, web, ioloop

class StatusWebSocket(websocket.WebSocketHandler):
    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print "WebSocket closed"


settings = {
    'auto_reload': True,
}

application = web.Application([
    (r'/', StatusWebSocket),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    ioloop.IOLoop.instance().start()

