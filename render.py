from rich import print
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress

from api import FloodWaitError
from models import Message


class Renderer:
    def __init__(self, message_count: int):
        self.progress = Progress()
        self.progress_task = self.progress.add_task(
            f"[cyan]Sending {message_count} messages...[/cyan]",
            total=message_count,
        )

        self.status = Panel(
            "[green]Running...[/green]",
            border_style="green",
        )

        self.live = Live(
            self._render(),
            refresh_per_second=10,
        )

    def _render(self) -> Group:
        return Group(
            self.progress,
            self.status,
        )

    def start(self) -> None:
        self.live.start()

    def stop(self) -> None:
        self.live.stop()

    def advance(self) -> None:
        self.progress.advance(self.progress_task)

    def render_rate_limit(
        self,
        error: FloodWaitError,
        limit_count: int,
    ) -> None:
        self.status = Panel.fit(
            f"[bold purple]Rate limit hit: {limit_count}[/bold purple]",
            border_style="purple",
        )

        self.live.update(self._render())

    def render_summary(
        self,
        messages: list[Message],
        limits_hit: int,
    ) -> None:
        wait_times = [
            message.wait_time
            for message in messages
            if message.wait_time is not None
        ]

        total_wait_time = sum(wait_times)
        average_wait_time = total_wait_time / len(wait_times)

        print(
            Panel(
                f"[bold cyan]Simulation Complete[/bold cyan]\n\n"
                f"Messages sent: {len(messages)}\n"
                f"Limits hit: {limits_hit}\n"
                f"Total wait time: {total_wait_time:.2f}s\n"
                f"Average wait time: {average_wait_time:.2f}s",
                border_style="green",
            )
        )