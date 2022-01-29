import time

import config
from TelegramBot.TelegramThread import TelegramThread, TelegramBot, MessageData
import CustomLogger


def hello(str_message: MessageData, bot: TelegramBot):
    bot.send_text(message="Hello dude!", chatroom_id=str_message.chatroom_id)


def reply_time(str_message: MessageData, bot: TelegramBot):
    bot.send_text(message=f"It is: {time.time()}", chatroom_id=str_message.chatroom_id)


def main():
    logger = CustomLogger.getLogger(level=10)

    telegram_thread = TelegramThread(bot_token=config.bot_token,
                                     chatroom_id=config.chatroom_id,
                                     logger=logger)
    telegram_thread.register_command("/hello", hello)
    telegram_thread.register_command("/time", reply_time)
    telegram_thread.start()
    telegram_thread.send_text(message="test")
    """with open("data/screenshot.png", "rb") as f:
        image = f.read()

    telegram_thread.send_photo(file=image)"""
    while True:
        message = telegram_thread.request_message()
        if message:
            print(message)
        time.sleep(0.1)
        pass


if __name__ == "__main__":
    main()
