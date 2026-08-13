import random
import time

from rich import print
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress

from api import FloodWaitError, TelegramAPI


MESSAGE_COUNT = 100
CHAT_COUNT = 10
MIN_SEND_INTERVAL = 0.01
MAX_SEND_INTERVAL = 0.05


class Bot:
    def __init__(self):
        self.api = TelegramAPI()

    def send_message(self, chat_id: int) -> None:
        self.api.process_message(chat_id)


class MessageSimulator:
    def __init__(self):
        self.bot = Bot()
        self.limits_hit = 0

    def run(self, message_count: int) -> None:
        with Progress() as progress, Live(refresh_per_second=10) as live:
            progress_task = progress.add_task(
                "[cyan]Sending messages...",
                total=message_count,
            )

            for message_index in range(message_count):
                chat_id = random.randint(1, CHAT_COUNT)

                self._send_message(
                    chat_id=chat_id,
                    message_index=message_index,
                    live=live,
                )

                progress.advance(progress_task)
                self._simulate_arrival_interval()

    def _send_message(
        self,
        chat_id: int,
        message_index: int,
        live: Live,
    ) -> None:
        while True:
            try:
                self.bot.send_message(chat_id)
                return

            except FloodWaitError as error:
                self.limits_hit += 1

                live.update(
                    Panel(
                        f"[blue]Hit limit at message {message_index}[/blue]\n"
                        f"[bold purple]Total limits hit: {self.limits_hit}[/bold purple]"
                    )
                )

                time.sleep(error.seconds)

    @staticmethod
    def _simulate_arrival_interval() -> None:
        time.sleep(random.uniform(MIN_SEND_INTERVAL, MAX_SEND_INTERVAL))


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
