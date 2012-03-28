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
    def ProcessMessage(message, client):
        requested_name = message.text
        if NickBot.isUsernameAvailable(requested_name):
            NickBot.RegisterClient(requested_name, client)
            NickBot.ConfirmToClient(client)
            print requested_name + " registered"
    
    @staticmethod    
    def RegisterClient(name, client):
        MessageServer.directory[name] = client
    
    @staticmethod
    def isUsernameAvailable(name):
        if name in MessageServer.directory:
            return False
        else:
            return True

    @staticmethod
    def ConfirmToClient(client):
        username = MessageServer.directory.key_for(client)
        forward_message = {"From" : "NickBot", "Message" : "OK"}
        json = MessageServer.coder.encode(forward_message)
        MessageServer.directory[username].write_message(json)


class GroupBot(Bot):
    """Creates and manages groups."""
    @staticmethod
    def ProcessMessage(message, client):
        username = MessageServer.directory.key_for(client)
        members = message.text.split(' ')
        members.append(username)
        name = GroupBot.RegisterGroup(members)
        GroupBot.ConfirmNameToClient(name, client)

    @staticmethod
    def RegisterGroup(client_list):
        group = []
        for client in client_list:
            if client in MessageServer.directory:
                group.append(client)
        if group:  # If group isn't empty
            group_name = "group" + str(MessageServer.group_id)
            MessageServer.group_id = MessageServer.group_id + 1
            MessageServer.groups[group_name] = group
            return group_name
        else:
            return None

    @staticmethod
    def ConfirmNameToClient(group_name, client):
        username = MessageServer.directory.key_for(client)
        forward_message = {"From" : "GroupBot", "Message" : group_name}
        json = MessageServer.coder.encode(forward_message)
        MessageServer.directory[username].write_message(json)

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
    def __init__(self, target, text):
        self.target = target
        self.text = text


class MessageDecoder:
    """Decodes JSON messages into our internal workable messages."""
    def decode(self, raw_message):
        # TODO: Validate JSON propperly.
        dic = json.loads(raw_message)
        message = Message(dic["To"], dic["Message"])
        return message

    def encode(self, message):
        # TODO: We should also validate the JSON we create
        json_message = json.dumps(message)
        return json_message


class MessageServer(tornado.websocket.WebSocketHandler):
    """Defines how the Server behaves."""
    group_id = 0
    directory = Bijection()  # Sometimes we know the connection and need a name
    groups = {}
    bots = {"GroupBot" : GroupBot}
    coder = MessageDecoder()

    def open(client):
        """Prints when a client opens a connection."""
        print "New WebSocket created and opened"

    def on_close(client):
        """Removes client from the directory."""
        if client in MessageServer.directory.values():
            username = MessageServer.directory.key_for(client)
            del MessageServer.directory[username]
            print username + " connection closing."
        else:
            pass  # We don't care about unregistered connections closing

    def on_message(client, raw_message):
        """Handles messages sent by clients."""
        message = MessageServer.coder.decode(raw_message)
        # If client isn't registered
        if client not in MessageServer.directory.values():  
            if message.target != "NickBot":  # and isn't trying to do so
                MessageServer.close(client)      # we close his connection
            else:                                # If he is, NickBot handles it
                NickBot.ProcessMessage(message, client)
        else:
            # If client is registered we check who he addresses
            # This Bot > Group > Client heriarchy adds some protection against
            # clients wanting to use names used by functions (bots or groups)
            # Bots are checked first since they extend functionality
            if message.target in MessageServer.bots:
                bot = message.target
                MessageServer.bots[bot].ProcessMessage(message, client)
            # We then check if it's a group 
            elif message.target in MessageServer.groups:
                group = MessageServer.groups[message.target]
                forward_message = {"From" : message.target, 
                                   "Message" : message.text}
                json = MessageServer.coder.encode(forward_message)
                for member in group:
                    MessageServer.directory[member].write_message(json)
            # Next we check if he addresses a client
            elif message.target in MessageServer.directory:
                # If he does we create a new message for the target
                # and we send it to them with reference to the sender
                username = MessageServer.directory.key_for(client)
                forward_message = {"From" : username, "Message" : message.text}
                json = MessageServer.coder.encode(forward_message)
                MessageServer.directory[message.target].write_message(json)
            else:
                pass  # We don't care


def main():
    """Creates instance of the server and starts IOLoop."""
    application = tornado.web.Application([(r"/ws", MessageServer), ])
    server = tornado.httpserver.HTTPServer(application)
    server.listen(8889)
    print "Listening now..."
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
