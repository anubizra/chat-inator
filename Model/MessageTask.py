class MessageTask(object):

    def __init__(self, message_channel, user_name, message):
        self.message_channel = message_channel
        self.user_name = user_name
        self.message = message

    def get_message(self):
        return '{}:{}'.format(self.user_name, self.message)
