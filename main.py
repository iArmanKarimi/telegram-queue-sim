import random
import time
from dataclasses import dataclass

from rich import print
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress

from api import FloodWaitError, TelegramAPI


MESSAGE_COUNT = 100
CHAT_COUNT = 10
MIN_SEND_INTERVAL = 0.01
MAX_SEND_INTERVAL = 0.05


@dataclass
class Message:
    index: int
    chat_id: int
    created_at: float
    sent_at: float | None = None

    @property
    def wait_time(self) -> float | None:
        if self.sent_at is None:
            return None

        return self.sent_at - self.created_at


class Bot:
    def __init__(self):
        self.api = TelegramAPI()

    def send_message(self, chat_id: int) -> None:
        self.api.process_message(chat_id)


class MessageSimulator:
    def __init__(self):
        self.bot = Bot()
        self.limits_hit = 0
        self.messages: list[Message] = []

    def run(self, message_count: int) -> None:
        with Progress() as progress, Live(refresh_per_second=10) as live:
            progress_task = progress.add_task(
                "[cyan]Sending messages...",
                total=message_count,
            )

            for message_index in range(message_count):
                message = self._create_message(message_index)

                self._send_message(
                    message=message,
                    live=live,
                )

                self.messages.append(message)

                progress.advance(progress_task)
                self._simulate_arrival_interval()

    def _create_message(self, message_index: int) -> Message:
        return Message(
            index=message_index,
            chat_id=random.randint(1, CHAT_COUNT),
            created_at=time.monotonic(),
        )

    def _send_message(
        self,
        message: Message,
        live: Live,
    ) -> None:
        while True:
            try:
                self.bot.send_message(message.chat_id)
                message.sent_at = time.monotonic()
                return

            except FloodWaitError as error:
                self.limits_hit += 1

                live.update(
                    Panel(
                        f"[blue]Hit limit at message {message.index}[/blue]\n"
                        f"[bold purple]Total limits hit: {self.limits_hit}[/bold purple]"
                    )
                )

                time.sleep(error.seconds)

    @staticmethod
    def _simulate_arrival_interval() -> None:
        time.sleep(
            random.uniform(
                MIN_SEND_INTERVAL,
                MAX_SEND_INTERVAL,
            )
        )


def main() -> None:
    print(
        Panel.fit(
            "[bold cyan]"
            "🔬 TELEGRAM: MESSAGE BROADCAST (RATE LIMIT SIMULATOR) 🔬"
            "[/bold cyan]",
            border_style="cyan",
        )
    )

    simulator = MessageSimulator()
    simulator.run(MESSAGE_COUNT)


if __name__ == "__main__":
    main()