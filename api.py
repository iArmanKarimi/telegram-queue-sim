import time


MESSAGE_SEND_LIMIT = 30
MESSAGE_SEND_LIMIT_PER_CHAT = 1


class FloodWaitError(Exception):
    code = 420

    def __init__(self, seconds: int, scope: str):
        self.seconds = seconds
        self.scope = scope

        super().__init__(
            f"FLOOD_WAIT_{seconds} ({scope})"
        )


class TelegramAPI:
    def __init__(self):
        self.messages: list[int] = []
        self.last_reset = time.monotonic()

    def _reset_window(self) -> None:
        now = time.monotonic()

        if now - self.last_reset >= 1:
            self.last_reset = now
            self.messages.clear()

    def _check_send_limit(self) -> None:
        if len(self.messages) >= MESSAGE_SEND_LIMIT:
            raise FloodWaitError(
                seconds=1,
                scope="global",
            )

    def _check_send_limit_per_chat(self, chat_id: int) -> None:
        if self.messages.count(chat_id) >= MESSAGE_SEND_LIMIT_PER_CHAT:
            raise FloodWaitError(
                seconds=1,
                scope="chat",
            )

    def process_message(self, chat_id: int) -> None:
        """
        Simulates sending a message to a chat.

        Raises FloodWaitError if the message cannot be sent
        because of a rate limit.
        """
        self._reset_window()
        self._check_send_limit()
        self._check_send_limit_per_chat(chat_id)
        self.messages.append(chat_id)
