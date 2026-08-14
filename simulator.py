import random
import time
from collections.abc import Callable

from bot import Bot
from models import Message


CHAT_COUNT = 5
MIN_SEND_INTERVAL = 0.01
MAX_SEND_INTERVAL = 0.05


class MessageSimulator:
    def __init__(
        self,
        bot: Bot,
        on_message_sent: Callable[[], None] | None = None,
    ):
        self.bot = bot
        self.on_message_sent = on_message_sent
        self.messages: list[Message] = []

    def run(self, message_count: int) -> list[Message]:
        for message_index in range(message_count):
            message = self._create_message(message_index)

            self.bot.send_message(message.chat_id)
            message.sent_at = time.monotonic()

            self.messages.append(message)

            if self.on_message_sent is not None:
                self.on_message_sent()

            self._simulate_arrival_interval()

        return self.messages

    @staticmethod
    def _create_message(message_index: int) -> Message:
        return Message(
            index=message_index,
            chat_id=random.randint(1, CHAT_COUNT),
            created_at=time.monotonic(),
        )

    @staticmethod
    def _simulate_arrival_interval() -> None:
        time.sleep(
            random.uniform(
                MIN_SEND_INTERVAL,
                MAX_SEND_INTERVAL,
            )
        )