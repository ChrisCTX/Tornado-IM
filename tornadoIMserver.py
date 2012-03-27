import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver

class Bot:
    """Interface / Abstract Bot, here just for clarity."""
    @staticmethod
    def ProcessMessage(message):
        raise NotImplementedError("Bot is just an abstract / interface")


class EchoBot(Bot):
    """Echos the message back to client."""
    @staticmethod
    def ProcessMessage(message):
        pass


class DirectoryBot(Bot):
    """Sends a message to the client with a list of all connected directory."""
    @staticmethod
    def ProcessMessage(message):
        pass


class NickBot(Bot):
    """Assigns a username to the client. SERVER ESSENTIAL."""
    @staticmethod    
    def ProcessMessage(message):
        pass
    
    @staticmethod    
    def RegisterClient(name, client):
        MessageServer.directory[name] = client
    
    @staticmethod
    def isUsernameAvailable(name):
        if name in MessageServer.directory:
            return False
        else:
            return True


class GroupBot(Bot):
    """Creates and manages groups."""
    @staticmethod
    def ProcessMessage(message):
        pass

    @staticmethod
    def RegisterGroup(client_list):
        group = []
        for client in client_list:
            if client in self.directory:
                group.append(client)
        if group:  # If group isn't empty
            group_name = "group" + str(MessageServer.group_id)
            MessageServer.group_id = MessageServer.group_id + 1
            MessageServer.directory[group_name] = group


class Bijection(dict):
    """Bijective dict. Each key maps to only one value (and vice-versa)."""
    def key_for(self, obj):
        """For the given value, return its corresponding key."""
        for key, val in self.iteritems():
            if val is obj:
                return key
        raise ValueError("The given object could not be found")


class MessageServer(tornado.websocket.WebSocketHandler):
    """Defines how the Server behaves."""
    group_id = 0
    directory = Bijection()
    bots = {"EchoBot" : EchoBot}

    def open(client):
        """Prints when a client opens a connection."""
        print "New WebSocket created and opened"

    def on_close(client):
        """Removes client from the directory."""
        if client in directory.values():
            username = directory.key_for(client)
            del MessageServer.directory[username]
            print username + " logged off."
        else:
            pass  # We don't care about unregistered connections closing

    def on_message(client, message):
        """Handles messages sent by clients."""
        # TODO: Decode message here
        if client not in directory.values():     # If client isn't registered
            if message.target is not "NickBot":  # and isn't trying to do so
                MessageServer.close(client)      # we close his connection
            else:                                # If he's trying to register
                NickBot.ProcessMessage(message)  # we let NickBot work it out
        else:
            pass


def main():
    """Creates instance of the server and starts IOLoop."""
    application = tornado.web.Application([(r"/ws", MessageServer), ])
    server = tornado.httpserver.HTTPServer(application)
    server.listen(8889)
    print "Listening now..."
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
