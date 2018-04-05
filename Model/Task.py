class Task(object):

    def __init__(self, command, sender, recipient, body):
        self.command = command
        self.sender = sender
        self.recipient = recipient
        self.body = body
