from collections import deque

from models import Message


class MessageQueue:
    def __init__(self):
        self.messages: deque[Message] = deque()

    def add(self, message: Message) -> None:
        self.messages.append(message)

    def get(self) -> Message:
        return self.messages.popleft()

    def __bool__(self) -> bool:
        return bool(self.messages)

    def __len__(self) -> int:
        return len(self.messages)
