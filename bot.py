import time
from collections.abc import Callable

from api import FloodWaitError, TelegramAPI


class Bot:
    def __init__(
        self,
        on_rate_limit: Callable[[FloodWaitError, int], None] | None = None,
    ):
        self.api = TelegramAPI()
        self.limits_hit = 0
        self.on_rate_limit = on_rate_limit

    def send_message(self, chat_id: int) -> None:
        while True:
            try:
                self.api.process_message(chat_id)
                return

            except FloodWaitError as error:
                self.limits_hit += 1

                if self.on_rate_limit is not None:
                    self.on_rate_limit(error, self.limits_hit)

                time.sleep(error.seconds)