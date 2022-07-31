import logging
import threading
from time import sleep
from queue import Queue

from TelegramBot.TelegramBot import TelegramBot, TelegramError, MessageData

log = logging.getLogger(__name__)


class TelegramThread(threading.Thread):
    def __init__(self, bot: TelegramBot,
                 queue_input: Queue = None):
        """
        :param bot:
        :param queue_input:
        """
        self.queue_input = queue_input if queue_input else Queue()

        self.bot = bot

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
            log.info(f"Unknown command: {data.command} in chatroom: {data.chatroom_id}")
            return
        log.info(f"Execute command {command}")
        for fn in self.commands[command]:
            fn(data, bot)

    def send_text(self, message: str, chatroom_id: str) -> None:
        self.queue_input.put((self.bot.send_text, (message, chatroom_id)))

    def send_photo(self, file: bytes, chatroom_id: str) -> None:
        self.queue_input.put((self.bot.send_photo, (file, chatroom_id)))

    def reconnect(self, max_sec: int = 120) -> None:
        sec_wait = 1
        while True:
            try:
                self.bot.request_bot_info()
                log.info(f"Reconnection successful!")
                break
            except ConnectionError:
                log.warning(f'Waiting for {sec_wait} seconds to retry.')
                sleep(sec_wait)
                sec_wait = min(max_sec, sec_wait * 2)  # limit waiting Time to max_sec

    def run(self):
        log.info("Start Telegram Thread.")
        message = None
        fn, data = None, None
        while True:
            try:
                sleep_flag = True

                if not message:
                    message = self.bot.request_message()

                if message:
                    log.info(f"Got Message '{message.last_message} from Sender '{message.sender_name} - {message.sender_id} ")
                    if message.command:
                        self._execute_commands(message.command, message, self.bot)
                    sleep_flag = False
                    message = None

                if not self.queue_input.empty() or data:
                    if not data:
                        fn, data = self.queue_input.get()
                    fn(*data)
                    self.queue_input.task_done()
                    fn, data = None, None
                    sleep_flag = False

                if sleep_flag:
                    sleep(1)

            except TelegramError as e:
                log.warning(e)
                log.warning(f"{e.error_code} - {e.description}")
                if e.error_code == 502:
                    self.reconnect(max_sec=1)
            except ConnectionError as e:
                log.warning(e)
                self.reconnect(max_sec=64)
            except Exception as e:
                log.exception(e)
                self.exception = e
                raise Exception(e)

    def get_exception(self):
        return self.exception
