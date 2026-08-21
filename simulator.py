import random
import time

from bot import Bot
from models import Message


CHAT_COUNT = 5
MIN_SEND_INTERVAL = 0.01
MAX_SEND_INTERVAL = 0.02


class MessageSimulator:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.messages: list[Message] = []
        self.duration = 0.0

    def run(self, message_count: int) -> list[Message]:
        started_at = time.monotonic()

        self.bot.start()

        for message_index in range(message_count):
            message = self._create_message(message_index)

            self.messages.append(message)
            self.bot.enqueue(message)

            self._simulate_arrival_interval()

        self.bot.stop()

        self.duration = time.monotonic() - started_at

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
