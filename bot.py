import threading
import time
from collections.abc import Callable

from api import FloodWaitError, TelegramAPI
from message_queue import MessageQueue
from models import Message


GLOBAL_SEND_INTERVAL = 1 / 30
CHAT_SEND_INTERVAL = 1.0


class Bot:
    def __init__(
        self,
        on_message_sent: Callable[[], None] | None = None,
        on_rate_limit: Callable[[FloodWaitError, int], None] | None = None,
        use_queue: bool = True,
    ):
        self.api = TelegramAPI()
        self.queue = MessageQueue()
        self.use_queue = use_queue

        self.limits_hit = 0

        self.on_message_sent = on_message_sent
        self.on_rate_limit = on_rate_limit

        self.chat_available_at: dict[int, float] = {}
        self.global_available_at = 0.0

        self.sender_thread: threading.Thread | None = None
        self.stop_requested = False

    def start(self) -> None:
        self.sender_thread = threading.Thread(
            target=(
                self._sender_loop
                if self.use_queue
                else self._naive_sender_loop
            ),
            name="telegram-sender",
        )
        self.sender_thread.start()

    def enqueue(self, message: Message) -> None:
        self.queue.add(message)

    def stop(self) -> None:
        self.stop_requested = True
        self.queue.close()

        if self.sender_thread is not None:
            self.sender_thread.join()

    def _sender_loop(self) -> None:
        while True:
            if self.stop_requested and not self.queue:
                return

            message = self.queue.pop_ready(self._is_ready)

            if message is not None:
                self._send(message)
                continue

            if self.stop_requested and not self.queue:
                return

            next_ready_at = self.queue.next_ready_at(
                self._next_ready_at,
            )

            if next_ready_at is None:
                self.queue.wait()
                continue

            sleep_time = max(
                0.0,
                next_ready_at - time.monotonic(),
            )

            self.queue.wait(sleep_time)

    def _naive_sender_loop(self) -> None:
        while True:
            if self.stop_requested and not self.queue:
                return

            message = self.queue.pop_ready(
                lambda _message, _now: True,
            )

            if message is None:
                self.queue.wait()
                continue

            self._send_naive(message)

    def _is_ready(
        self,
        message: Message,
        now: float,
    ) -> bool:
        chat_ready_at = self.chat_available_at.get(
            message.chat_id,
            0.0,
        )

        return (
            chat_ready_at <= now
            and self.global_available_at <= now
        )

    def _next_ready_at(self, message: Message) -> float:
        chat_ready_at = self.chat_available_at.get(
            message.chat_id,
            0.0,
        )

        return max(
            chat_ready_at,
            self.global_available_at,
        )

    def _send(self, message: Message) -> None:
        try:
            self.api.process_message(message.chat_id)

        except FloodWaitError as error:
            self.limits_hit += 1

            if self.on_rate_limit is not None:
                self.on_rate_limit(
                    error,
                    self.limits_hit,
                )

            self._handle_unexpected_rate_limit(
                message,
                error,
            )

            return

        now = time.monotonic()

        message.sent_at = now

        self.chat_available_at[message.chat_id] = (
            now + CHAT_SEND_INTERVAL
        )

        self.global_available_at = (
            now + GLOBAL_SEND_INTERVAL
        )

        if self.on_message_sent is not None:
            self.on_message_sent()

    def _send_naive(self, message: Message) -> None:
        while True:
            try:
                self.api.process_message(message.chat_id)

            except FloodWaitError as error:
                self.limits_hit += 1

                if self.on_rate_limit is not None:
                    self.on_rate_limit(
                        error,
                        self.limits_hit,
                    )

                time.sleep(error.seconds)
                continue

            message.sent_at = time.monotonic()

            if self.on_message_sent is not None:
                self.on_message_sent()

            return

    def _handle_unexpected_rate_limit(
        self,
        message: Message,
        error: FloodWaitError,
    ) -> None:
        retry_at = time.monotonic() + error.seconds

        if getattr(error, "scope", "chat") == "global":
            self.global_available_at = max(
                self.global_available_at,
                retry_at,
            )
        else:
            self.chat_available_at[message.chat_id] = max(
                self.chat_available_at.get(
                    message.chat_id,
                    0.0,
                ),
                retry_at,
            )

        self.queue.add(message)
