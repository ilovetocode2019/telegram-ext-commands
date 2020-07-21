from telegram.ext import Updater, CommandHandler
import importlib
import inspect

from .core import Command, Cog
from .errors import NotFound, CommandAlreadyExists, LoadError

class Bot:
    """Represent a telegram bot"""

    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.commands_dict = {}
        self._handlers = {}

        self.cogs_dict = {}

    def command(self, *args, **kwargs):
        """Turns a function into a command"""

        def deco(func):
            name = kwargs.get("name") or func.__name__
            if name in self.commands_dict:
                raise CommandAlreadyExists("A command with that name already exists")

            command = Command(func, **kwargs)
            
            handler = CommandHandler(name, command.invoke)
            self.dispatcher.add_handler(handler)

            self._handlers[name] = handler
            self.commands_dict[name] = command

            return command
        
        return deco

    def add_command(self, func, **kwargs):
        """Adds a function as a command"""

        name = kwargs.get("name") or func.__name__
        if name in self.commands_dict:
            raise CommandAlreadyExists("A command with that name already exists")

        command = Command(func, **kwargs)

        handler = CommandHandler(name, command.invoke)
        self.dispatcher.add_handler(handler)

        self._handlers[name] = handler
        self.commands_dict[name] = command

        return command
    def remove_command(self, name):
        """Removes a command"""

        if name not in self.commands:
            raise NotFound("No command by that name")
            return

        self.dispatcher.remove_handler(self._handlers[name])
        self._handlers.pop(name)
        self.commands_dict.pop(name)

    @property
    def commands(self):
        """A list of commands in the bot"""

        return list(self.commands_dict.values())

    def load_extension(self, location):
        """Loads an extension into the bot"""

        cog = importlib.import_module(location)

        if not hasattr(cog, "setup"):
            raise LoadError("No setup function")

        cog.setup(self)

    def remove_cog(self, location):
        """Removes and extension from the bot"""

        if location not in self.cogs_dict:
            raise NotFound("Cog is not loaded")

        for command in self.cogs_dict[location].commands:
            self.remove_command(command.name)

    def add_cog(self, cog):
        cog_commands = []
        for command in dir(cog):
            command = getattr(cog, command)
            if isinstance(command, Command):
                command.cog = cog
                
                self.commands_dict[command.name] = command
                cog_commands.append(command)

                handler = CommandHandler(command.name, command.invoke)
                self._handlers[command.name] = handler

                self.dispatcher.add_handler(handler)

        self.cogs_dict[cog.__class__.__name__] = Cog(cog.__class__.__name__, cog_commands)

    @property
    def cogs(self):
        return list(self.cogs_dict.values())

    def run(self, idle=True):
        """Runs the bot"""

        self.updater.start_polling()

        if idle:
            self.updater.idle()