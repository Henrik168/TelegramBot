import logging
import threading
from time import sleep
from queue import Queue

from TelegramBot.TelegramBot import TelegramBot, TelegramError, MessageData
import CustomLogger


class TelegramThread(threading.Thread):
    def __init__(self, bot_token: str,
                 chatroom_id: str,
                 logger: logging.Logger = None,
                 queue_input: Queue = None):
        """

        :param bot_token:
        :param chatroom_id:
        :param logger:
        :param queue_input:
        """
        self.bot_token = bot_token
        self.chatroom_id = chatroom_id
        self.logger = logger if logger else CustomLogger.getLogger()
        self.queue_input = queue_input if queue_input else Queue()

        self.bot = TelegramBot(bot_token=self.bot_token,
                               logger=self.logger)

        self.commands = dict()

        threading.Thread.__init__(self)
        self.daemon = True
        self.exception = None

    def register_command(self, command: str, fn):
        if command not in self.commands:
            self.commands[command] = []
        self.commands[command].append(fn)

    def _execute_commands(self, command: str, data: MessageData, bot: TelegramBot):
        if command not in self.commands:
            self.bot.send_text(f"Unknown command: {data.command}", chatroom_id=data.chatroom_id)
            return
        for fn in self.commands[command]:
            fn(data, bot)

    def send_text(self, message: str, chatroom_id: str = None) -> None:
        chatroom_id = chatroom_id if chatroom_id else self.chatroom_id
        self.queue_input.put((self.bot.send_text, (message, chatroom_id)))

    def send_photo(self, file: bytes, chatroom_id: str = None) -> None:
        chatroom_id = chatroom_id if chatroom_id else self.chatroom_id
        self.queue_input.put((self.bot.send_photo, (file, chatroom_id)))

    def reconnect(self, max_sec: int = 120) -> None:
        sec_wait = 1
        while True:
            try:
                self.bot.request_bot_info()
                self.logger.info(f"Reconnection successful!")
                self.bot.send_text(f"Reconnection to Telegram successful!", self.chatroom_id)
                break
            except ConnectionError:
                self.logger.warning(f'Waiting for {sec_wait} seconds to retry.')
                sleep(sec_wait)
                sec_wait = min(max_sec, sec_wait * 2)  # limit waiting Time to max_sec

    def run(self):
        self.logger.info("Start Telegram Thread.")

        while True:
            try:
                sleep_flag = True

                message = self.bot.request_message()
                if message:
                    if message.command:
                        self._execute_commands(message.command, message, self.bot)
                    sleep_flag = False

                if not self.queue_input.empty():
                    fn, data = self.queue_input.get()
                    fn(*data)
                    self.queue_input.task_done()
                    sleep_flag = False

                if sleep_flag:
                    sleep(1)

            except TelegramError as e:
                self.logger.warning(e)
            except ConnectionError as e:
                self.logger.warning(e)
                self.reconnect(max_sec=64)
            except Exception as e:
                self.logger.exception(e)
                self.exception = e
                raise Exception(e)

    def get_exception(self):
        return self.exception
