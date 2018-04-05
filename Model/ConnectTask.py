class ConnectTask(object):

    def __init__(self, service_name, service_config, discord_channel):
        self.service_name = service_name
        self.service_config = service_config
        self.discord_channel = discord_channel
