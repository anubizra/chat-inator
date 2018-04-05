"""Discord Bot Entry Point"""
import os
import config
from multiprocessing import Queue
from Workers.DiscordService import DiscordService

if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(__file__))
    config = config.get_config("config.json")
    config["root"] = root

    services = {}

    queues = {}
    queues['DISCORD'] = Queue()
    queues['TWITCH'] = Queue()
    queues['YOUTUBE'] = Queue()

    # start the bot
    discord_service = DiscordService(config, queues, services)
    discord_service.run(config['DiscordBotToken'])

    # shutdown once all processes finish
    for name, queue in queues.items():
        queue.close()
        queue.join_thread()

    for service_name, service in services.items():
        service.join()
