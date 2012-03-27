import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
import json

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
    """Sends a message to the client with a list of all connected clients."""
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


class Message:
    """Internal message."""
    def __init__(target, text):
        self.target = target
        self.text = text

class MessageDecoder:
    """Decodes JSON messages into our internal workable messages."""
    def decode(raw_message):
        # TODO: Validate JSON propperly.
        dic = json.loads(raw_message)
        message = message(dic["To"], dic["Message"])
        return message

    def encode(message):
        # TODO: We should also validate the JSON we create
        json_message = json.dumps(message)
        return json_message

class MessageServer(tornado.websocket.WebSocketHandler):
    """Defines how the Server behaves."""
    group_id = 0
    directory = Bijection()
    bots = {"EchoBot" : EchoBot}
    coder = MessageDecoder()

    def open(client):
        """Prints when a client opens a connection."""
        print "New WebSocket created and opened"

    def on_close(client):
        """Removes client from the directory."""
        if client in MessageServer.directory.values():
            username = MessageServer.directory.key_for(client)
            del MessageServer.directory[username]
            print username + " logged off."
        else:
            pass  # We don't care about unregistered connections closing

    def on_message(client, raw_message):
        """Handles messages sent by clients."""
        message = MessageServer.coder.decode(raw_message)
        # If client isn't registered
        if client not in MessageServer.directory.values():     
            if message.target is not "NickBot":  # and isn't trying to do so
                MessageServer.close(client)      # we close his connection
            else:                                # If he's trying to register
                NickBot.ProcessMessage(message)  # we let NickBot work it out
        else:
            # If client is registered we check who he addresses
            # Bots are checked first since they extend functionality
            if message.target in MessageServer.bots:
                MessageServer.bots[message.target].ProcessMessage(message)
            # Next we check if he addresses a client
            elif message.target in MessageServer.directory:
                # If he does we create a new message for the target
                # and we send it to them with reference to the sender
                username = MessageServer.directory.key_for(client)
                forward_message = Message(username, message.text)
                json = MessageServer.coder.encode(forward_message)
                MessageServer.directory[message.target].write_message(json)


def main():
    """Creates instance of the server and starts IOLoop."""
    application = tornado.web.Application([(r"/ws", MessageServer), ])
    server = tornado.httpserver.HTTPServer(application)
    server.listen(8889)
    print "Listening now..."
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
