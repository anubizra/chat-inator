import time
from threading import Thread
from multiprocessing import Process
import Service.YouTube.Auth as YouTubeAuth
import Service.YouTube.API as YouTube
from Model.Task import Task
from Model.MessageTask import MessageTask

class YouTubeWorker(Process):

    def __init__(self, config, queues, discord_channel):
        Process.__init__(self)
        self.config = config
        self.queues = queues
        self.discord_channel = discord_channel
        self.client = None
        self.broadcast_id = None
        self.broadcast_title = None
        self.live_chat_id = None

    def run(self):
        client_secret_file = '{}/{}'.format(self.config["root"], self.config["YouTube"]["ClientSecret"])

        print('Please authenticate your YouTube Owner account. This is the account you stream as.')
        youtuber_client = YouTubeAuth.get_authenticated_service('YouTuber', client_secret_file)
        print('YouTube Owner Account Authenticated.')

        broadcast_info = YouTube.get_live_broadcast(youtuber_client)
        self.broadcast_id = broadcast_info['id']
        self.broadcast_title = broadcast_info['title']
        self.live_chat_id = broadcast_info['liveChatId']

        print('Please authenticate your YouTube Bot account. This is the account you want the bot to post messages as.')
        self.client = YouTubeAuth.get_authenticated_service('Bot', client_secret_file)
        print('YouTube Bot Account Authenticated.')

        print('Connected to Stream: {}'.format(broadcast_info['title']))

        thread = Thread(
            target=self.start_listening,
            args=(client_secret_file, self.live_chat_id, self.queues,)
        )
        thread.daemon = True
        thread.start()

        self.monitor_queue()

    def start_listening(self, client_secret_file, live_chat_id, queues):
        client = YouTubeAuth.get_authenticated_service('Bot', client_secret_file)
        print('YouTube Listener Connected')
        next_page_token = None
        while True:
            response = YouTube.get_live_chat_messages(client, live_chat_id, next_page_token)
            for chat_message in YouTube.get_live_chat_message(response['chat_messages']):
                chat_user = chat_message['user']
                if (chat_user != 'AnubizBot'):
                    chat_text = chat_message['message']
                    new_message = MessageTask(self.discord_channel, chat_user, chat_text)
                    new_task = Task('MESSAGE', 'YOUTUBE', 'DISCORD', new_message)
                    print('YOUTUBE -> DISCORD: {}'.format(new_message.get_message()))
                    queues['DISCORD'].put(new_task, False)

            next_page_token = response['next_page_token']
            polling_interval_seconds = response['polling_interval_seconds']
            time.sleep(polling_interval_seconds)


    def monitor_queue(self):
        while True:
            task = self.queues['YOUTUBE'].get()

            if task.command == 'MESSAGE':
                print('received from {}: {}'.format(task.sender, task.body.get_message()))
                self.post_message(task.body.get_message())

            else:
                print("YOUTUBE WORKER: Unknown Command: {}".format(task.command))

    def post_message(self, message):
        YouTube.post_message(self.client, self.live_chat_id, message)
