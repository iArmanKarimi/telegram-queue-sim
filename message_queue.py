import threading
import time
from collections import deque
from collections.abc import Callable

from models import Message


class MessageQueue:
    def __init__(self):
        self.messages: deque[Message] = deque()
        self.condition = threading.Condition()
        self.closed = False

    def add(self, message: Message) -> None:
        with self.condition:
            self.messages.append(message)
            self.condition.notify()

    def pop_ready(
        self,
        is_ready: Callable[[Message, float], bool],
    ) -> Message | None:
        with self.condition:
            now = time.monotonic()
            message_count = len(self.messages)

            for _ in range(message_count):
                message = self.messages.popleft()

                if is_ready(message, now):
                    return message

                self.messages.append(message)

            return None

    def next_ready_at(
        self,
        ready_at: Callable[[Message], float],
    ) -> float | None:
        with self.condition:
            if not self.messages:
                return None

            return min(
                ready_at(message)
                for message in self.messages
            )

    def wait(self, timeout: float | None = None) -> None:
        with self.condition:
            self.condition.wait(timeout)

    def close(self) -> None:
        with self.condition:
            self.closed = True
            self.condition.notify_all()

    def __len__(self) -> int:
        with self.condition:
            return len(self.messages)

    def __bool__(self) -> bool:
        return len(self) > 0
