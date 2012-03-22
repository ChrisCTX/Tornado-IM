import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """Defines how the WebSocket behaves."""
    clients = []

    def open(self):
        """On succesful connection adds client to list and welcomes them."""
        WebSocketHandler.clients.append(self)
        self.write_message("Connection established, Welcome!")
        print "New WebSocket created and opened"

    def on_close(self):
        """Removes client from list."""
        WebSocketHandler.clients.remove(self)
        print "WebSocket closed"

    def on_message(self, message):
        """When a client sends a message, its passed to all other clients."""
        for client in WebSocketHandler.clients:
            if client is not self:
                client.write_message(message)
        print str(message)


def main():
    """Creates instance of the server and starts IOLoop."""
    application = tornado.web.Application([(r"/ws", WebSocketHandler), ])
    server = tornado.httpserver.HTTPServer(application)
    server.listen(8888)
    print "Listening now..."
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
