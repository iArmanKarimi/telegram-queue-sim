import time
from collections.abc import Callable

from api import FloodWaitError, TelegramAPI
from message_queue import MessageQueue
from models import Message


class Bot:
    def __init__(
        self,
        on_rate_limit: Callable[[FloodWaitError, int], None] | None = None,
    ):
        self.api = TelegramAPI()
        self.queue = MessageQueue()
        self.limits_hit = 0
        self.on_rate_limit = on_rate_limit

    def enqueue(self, message: Message) -> None:
        self.queue.add(message)

    def process_queue(self) -> None:
        messages_to_process = len(self.queue)

        for _ in range(messages_to_process):
            message = self.queue.get()

            try:
                self.api.process_message(message.chat_id)
                message.sent_at = time.monotonic()

            except FloodWaitError as error:
                self.limits_hit += 1

                if self.on_rate_limit is not None:
                    self.on_rate_limit(error, self.limits_hit)

                self.queue.add(message)
