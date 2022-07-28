import logging
import os
from dataclasses import dataclass
from typing import Optional
import TelegramBot.lib_requests as lib_requests

log = logging.getLogger()


@dataclass
class MessageData:
    last_message: str
    chatroom_id: str
    sender_id: str
    sender_name: str

    @property
    def command(self):
        if not self.last_message[:1] == "/":
            return
        if "@" in self.last_message:
            return self.last_message.split("@")[0]
        elif " " in self.last_message:
            return self.last_message.split(" ")[0]
        else:
            return self.last_message


class TelegramError(Exception):
    def __init__(self, text: str, chatroom_id: str = 0):
        self.text = text,
        self.chatroom_id = chatroom_id


class TelegramBot:
    def __init__(self, bot_token: str):
        """
        :param bot_token:
        """
        self.bot_token = bot_token
        self.url = "https://api.telegram.org/bot" + self.bot_token
        self.update_id = 0

    def request_bot_info(self) -> dict:
        """Request Bot Info"""
        result = lib_requests.http_request(self.url + "/getMe")
        if not result["result"]["username"]:
            raise TelegramError('Missing data result["result"]["username"]')
        log.debug(f"Request Bot Info: {result}")
        return result["result"]["username"]

    def send_text(self, message: str, chatroom_id: str) -> None:
        """Send Text Message"""
        params = {"chat_id": chatroom_id, "text": message}
        result = lib_requests.http_request(self.url + "/sendMessage", params)
        if not result["ok"]:
            raise TelegramError(f"Error sending Text Message: {message} to Chatroom{chatroom_id}")
        log.debug(f"Send Text Message: {message} to Chatroom {chatroom_id}")

    def send_photo(self, file: bytes, chatroom_id: str) -> None:
        if not file:
            raise TelegramError(f"Got not bytes Object to send a photo.")
        # send file to chat
        params = {"chat_id": chatroom_id}
        payload = {"photo": file}
        result = lib_requests.http_request(self.url + "/sendPhoto", params, payload)

        if not result["ok"]:
            self.send_text(result["description"], chatroom_id)
            raise TelegramError(f"Error sending Photo to Chatroom: {chatroom_id} Response: {result}")
        log.debug(f"Send Photo to chat: {chatroom_id}")

    def send_document(self, file_path: str, chatroom_id: str) -> None:
        """Send Text Message"""
        if not os.path.isfile(file_path):
            raise TelegramError(f"File '{file_path}' does not exists.")

        params = {"chat_id": chatroom_id}
        files = {"document": open(file=file_path, mode="rb")}
        result = lib_requests.http_request(self.url + "/sendDocument", params=params, files=files)

        if not result["ok"]:
            log.error(result)
            raise TelegramError(f"Error sending Document '{file_path}' to Chatroom{chatroom_id}")

        log.debug(f"Send Document '{file_path}' to Chatroom {chatroom_id}")

    def request_message(self) -> Optional[MessageData]:
        """
        Request Last messages.
        :return:
        """
        params = {"offset": self.update_id + 1}
        response = lib_requests.http_request(self.url + "/getUpdates", params)

        if not response["ok"]:
            raise TelegramError(f"Failure in Response: {response}")

        if len(response["result"]) == 0:
            return

        # store messages to list of MessageData
        message = response["result"][0]
        log.debug(f"Got message: {message}")

        # store last update ID for requesting just newer Messages
        self.update_id = message["update_id"]

        if "message" not in message.keys():
            raise TelegramError(f"Not a Text Message {message}", chatroom_id=message["message"]["chat"]["id"])
        if "text" not in message["message"].keys():
            raise TelegramError(f"Not a Text Message {message}", chatroom_id=message["message"]["chat"]["id"])

        return MessageData(last_message=str(message["message"]["text"]),
                           chatroom_id=str(message["message"]["chat"]["id"]),
                           sender_id=str(message["message"]["from"]["id"]),
                           sender_name=str(message["message"]["from"]["first_name"])
                           )
