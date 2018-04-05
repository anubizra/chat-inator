import time
import socket
from threading import Thread
from multiprocessing import Process, Queue, current_process
from Model.Task import Task
from Model.MessageTask import MessageTask

class TwitchWorker(Process):

    def __init__(self, config, queues, discord_channel):
        Process.__init__(self)
        self.socket = None
        self.queues = queues
        self.discord_channel = discord_channel
        self.host = config['Twitch']['Host']
        self.port = config['Twitch']['Port']
        self.token = config['Twitch']['OAuthToken']
        self.nickname = config['Twitch']['Nickname']
        self.channel = config['Twitch']['Channel']

    def run(self):
        self.connect()
        self.join_chat()

        thread = Thread(target=self.start_listening, args=(self.socket, self.queues,))
        thread.daemon = True
        thread.start()

        self.monitor_queue()

    def connect(self):
        self.socket = socket.socket()
        self.socket.connect((self.host, self.port))
        self.socket.send("PASS {}\r\n".format(self.token).encode())
        self.socket.send("NICK {}\r\n".format(self.nickname).encode())
        self.socket.send("JOIN #{}\r\n".format(self.channel).encode())
        print("Connected")

    def join_chat(self):
        readbuffer = ""
        loading = True
        while loading:
            readbuffer = readbuffer + self.socket.recv(1024).decode()
            temp = str.split(readbuffer, "\n")
            readbuffer = temp.pop()
            for line in temp:
                print(line)
                loading = self.loading_complete(line)
        self.post_message("Successfully joined chat")
        print("Joined")

    def start_listening(self, socket, queues):
        readbuffer = ""
        while True:
            readbuffer = readbuffer + socket.recv(1024).decode()
            temp = str.split(readbuffer, "\n")
            readbuffer = temp.pop()
            for line in temp:
                print(line)
                if "PING" in line:
                    socket.send(line.replace("PING", "PONG").encode())
                    continue

                separate = line.split(":", 2)
                user = separate[1].split("!", 1)[0]

                separate = line.split(":", 2)
                message = separate[2]

                new_message = MessageTask(self.discord_channel, user, message)
                new_task = Task('MESSAGE', 'TWITCH', 'DISCORD', new_message)

                print('TWITCH -> DISCORD: {}'.format(message))
                queues['DISCORD'].put(new_task, False)

    def monitor_queue(self):
        while True:
            task = self.queues['TWITCH'].get()

            if task.command == 'MESSAGE':
                print('received from {}: {}'.format(task.sender, task.body.get_message()))
                self.post_message(task.body.get_message())

            else:
                print("TWITCH SENDER: Unknown Command: {}".format(task.command))

    def loading_complete(self, line):
        if "End of /NAMES list" in line:
            return False
        else:
            return True

    def post_message(self, message):
        messageTemp = "PRIVMSG #" + self.channel + " :" + message
        self.socket.send((messageTemp + "\r\n").encode())
        print("Sent: " + messageTemp)
