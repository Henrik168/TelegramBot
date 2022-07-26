import time

import config
from TelegramBot.TelegramThread import TelegramThread, TelegramBot, MessageData
import CustomLogger

log = CustomLogger.getLogger(level=20)


def hello(message: MessageData, bot: TelegramBot):
    bot.send_text(message="Hello dude!", chatroom_id=message.chatroom_id)
    log.info(f"Send text 'Hello dude!' to chatroom: {message.chatroom_id}")


def reply_time(message: MessageData, bot: TelegramBot):
    bot.send_text(message=f"It is: {time.time()}", chatroom_id=message.chatroom_id)
    log.info(f"Send text 'It is: {time.time()}' to chatroom: {message.chatroom_id}")


def send_photo(message: MessageData, bot: TelegramBot):
    with open("./screenshot.png", "rb") as f:
        image = f.read()
    bot.send_photo(file=image, chatroom_id=message.chatroom_id)
    log.info(f"Send Photo to chatroom: {message.chatroom_id}")


def main():
    telegram_bot = TelegramBot(bot_token=config.bot_token)
    telegram_bot.send_text(message="Telegrambot set up.", chatroom_id=config.chatroom_id)
    log.info("Bot set up.")

    telegram_thread = TelegramThread(bot=telegram_bot)
    telegram_thread.register_command("/hello", hello)
    telegram_thread.register_command("/time", reply_time)
    telegram_thread.register_command("/photo", send_photo)
    telegram_thread.start()
    telegram_thread.send_text(message="Thread set up.", chatroom_id=config.chatroom_id)
    log.info("Thread set up.")

    while True:
        time.sleep(0.1)
        pass


if __name__ == "__main__":
    main()
