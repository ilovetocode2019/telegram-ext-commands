class Context:
    """Context in a command"""

    def __init__(self, command, **kwargs):
        self.command = command
        self.bot = command.bot

        self.message = kwargs.get("message")
        self.chat = kwargs.get("chat")
        self.author = kwargs.get("author")
        self.args = kwargs.get("args")
        self.kwargs = kwargs.get("kwargs")

    def send(self, content, parse_mode=None):
        """Shortcut for bot.send_message"""

        return self.bot.updater.bot.send_message(chat_id=self.chat.id, text=content, parse_mode=parse_mode)

    def reply(self, content):
        """Replys to the message"""

        return self.message.reply_text(content, reply=self.message.message_id)