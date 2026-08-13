from api import TelegramAPI, FloodWaitError
import time
import random
from rich import print
from rich.panel import Panel
from rich.progress import Progress
from rich.live import Live


print(
    Panel.fit(
        "[bold cyan]🔬 TELEGRAM MESSAGE BROADCAST RATE LIMIT SIMULATOR 🔬[/bold cyan]",
        border_style="cyan",
    )
)


api = TelegramAPI()


class Bot:
    def __init__(self, api: TelegramAPI):
        self.api = api

    def send_message(self, chat_id):
        self.api.process_message(chat_id)


class MessageSimulator:
    def __init__(self, bot: Bot):
        self.bot = bot

    def run(self, message_count=100):
        with Progress() as progress:
            progress_task = progress.add_task(
                "[cyan]Sending messages...",
                total=message_count,
            )

            limits_hit = 0

            with Live(refresh_per_second=10) as live:
                for message_index in range(message_count):
                    chat_id = random.randint(1, 10)

                    progress.update(progress_task, advance=1)

                    while True:
                        try:
                            self.bot.send_message(chat_id)
                            break

                        except FloodWaitError as error:
                            limits_hit += 1

                            live.update(
                                Panel(
                                    f"[blue]Hit limit at message {message_index}[/blue]\n"
                                    f"[bold purple]Total limits hit: {limits_hit}[/bold purple]"
                                )
                            )

                            time.sleep(error.seconds)


bot = Bot(api)
simulator = MessageSimulator(bot)
simulator.run()