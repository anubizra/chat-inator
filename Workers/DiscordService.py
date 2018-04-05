import discord
import traceback
import asyncio
from threading import Thread
from Model.ConnectTask import ConnectTask
from Model.MessageTask import MessageTask
from Model.Task import Task
from Workers.TwitchWorker import TwitchWorker
from Workers.YouTubeWorker import YouTubeWorker

class DiscordService(discord.Client):

    def __init__(self, config, queues, services):
        discord.Client.__init__(self)
        self.config = config
        self.queues = queues
        self.services = services

    async def on_ready(self):
        print('Discord Worker Started | Logged in as {0} ({1})'.format(self.user.name, self.user.id))

        self.chat_services = {}
        self.chat_services['TWITCH'] = TwitchWorker
        self.chat_services['YOUTUBE'] = YouTubeWorker

        thread = Thread(target=self.wait_for_messages, args=(self, self.queues,))
        thread.daemon = True
        thread.start()

    async def on_error(self, event, *args, **kwargs):
        message = args[0]  # Gets the message object
        trace = traceback.format_exc()
        print('DISCORD ERROR: \n{}\n{}'.format(message, trace))
        #await self.send_message(message.channel, "You caused an error!")
        self.on_error(event, *args, **kwargs)

    async def on_message(self, message):
        if not message.content.startswith("!"):
            return

        message_args = message.content.split(" ")
        command = message_args.pop(0)
        if command == '!connect':
            chat_service_name = message_args.pop(0).upper()
            await self.send_message(
                message.channel, 'Connecting to {} Chat Service...'.format(chat_service_name)
            )
            body = ConnectTask(chat_service_name, self.config, message.channel)
            task = Task('CONNECT', 'DISCORD', 'DISCORD', body)

            print('')
            print('send to DISCORD: CONNECT')
            self.queues['DISCORD'].put(task, False)

        elif command == '!send':
            message_text = ''.join(message_args)
            body = MessageTask('DISCORD', 'bot', message_text)

            twitch_task = Task('MESSAGE', 'DISCORD', 'TWITCH', body)
            print('')
            print('DISCORD -> TWITCH: {}'.format(message_text))
            self.queues['TWITCH'].put(twitch_task, False)

            youtube_task = Task('MESSAGE', 'DISCORD', 'YOUTUBE', body)
            print('')
            print('DISCORD -> YOUTUBE: {}'.format(message_text))
            self.queues['YOUTUBE'].put(youtube_task, False)

        elif command == '!blah':
            message_text = ''.join(message_args)
            new_message = MessageTask(message.channel, 'bot', message_text)
            new_task = Task('MESSAGE', 'DISCORD', 'DISCORD', new_message)

            print('')
            print('send to DISCORD: {}'.format(message_text))
            self.queues['DISCORD'].put(new_task, False)

    def wait_for_messages(self, client, queues):
        while True:
            task = self.queues['DISCORD'].get()

            if task.command == 'QUIT':
                #todo: stop all workers and exit
                pass

            elif task.command == 'CONNECT':
                print('received from {}: CONNECT'.format(task.sender))

                service_name = task.body.service_name
                service_config = task.body.service_config
                discord_channel = task.body.discord_channel

                if (service_name in self.chat_services.keys()):
                    chat_worker = self.chat_services[service_name](service_config, queues, discord_channel)
                    chat_worker.start()
                    self.services[service_name] = chat_worker

            elif task.command == 'MESSAGE':
                if (task.recipient != 'DISCORD'):
                    recipient = 'YOUTUBE' if task.sender == 'TWITCH' else 'TWITCH'
                    relay_task = Task('MESSAGE', task.sender, recipient, task.body)
                    print('{} -> {}: {}'.format(task.sender, recipient, relay_task.body.get_message()))
                    self.queues[recipient].put(relay_task, False)

                print('received from {}: {}'.format(task.sender, task.body.get_message()))
                asyncio.run_coroutine_threadsafe(
                    client.send_message(
                        task.body.message_channel,
                        task.body.get_message()),
                        client.loop
                    ).result()

            else:
                print("DISCORD SENDER: Unknown Command: {}".format(task.command))
