import time

from rich import print
from rich.align import Align
from rich.console import Group
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

from api import FloodWaitError
from models import Message


class Renderer:
    def __init__(self, message_count: int, mode: str = "QUEUE-AWARE"):
        self.message_count = message_count
        self.mode = mode
        self.sent_count = 0
        self.limits_hit = 0
        self.started_at = time.monotonic()
        self.finished_at: float | None = None
        self.last_event = "Waiting for sender..."
        self.delivery_times: list[float] = []

        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(
                bar_width=None,
                complete_style="cyan",
                finished_style="green",
                pulse_style="yellow",
            ),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            expand=True,
        )
        self.progress_task = self.progress.add_task(
            "Delivering messages",
            total=message_count,
        )

        self.status = Panel(
            (
                "[green]Broadcast in progress[/green]\n"
                "The queue is selecting the next ready chat."
                if mode == "QUEUE-AWARE"
                else "[yellow]Blocking sender in progress[/yellow]\n"
                "The current message holds the FIFO until it succeeds."
            ),
            title=" LIVE STATUS ",
            title_align="left",
            border_style="green",
            padding=(1, 2),
        )

        self.live = Live(
            self._render(),
            refresh_per_second=10,
            vertical_overflow="crop",
        )

    def _render(self) -> Layout:
        header = Panel(
            Align.center(
                Text.from_markup(
                    "[bold cyan]TELEGRAM[/bold cyan] "
                    "[dim]//[/dim] [bold white]QUEUE SIM[/bold white] "
                    f"[dim]//[/dim] [bold]{self.mode}[/bold]"
                )
            ),
            border_style="cyan",
            padding=(0, 1),
        )

        progress_panel = Panel(
            Group(
                self.progress,
                self._live_delivery_chart(),
            ),
            title=" DELIVERY PIPELINE ",
            title_align="left",
            border_style="cyan",
            padding=(1, 2),
        )

        stats = Table.grid(padding=(0, 2))
        stats.add_column(style="dim")
        stats.add_column(justify="right", style="bold white")
        stats.add_row("Sent", f"{self.sent_count}/{self.message_count}")
        stats.add_row("Limits hit", str(self.limits_hit))
        stats.add_row("Elapsed", f"{self._elapsed():.1f}s")
        stats.add_row("Send rate", f"{self._send_rate():.1f} msg/s")

        telemetry_panel = Panel(
            stats,
            title=" TELEMETRY ",
            title_align="left",
            border_style="blue",
            padding=(1, 1),
        )

        right_column = Layout(name="right_column")
        right_column.split_column(
            Layout(self.status, ratio=1),
            Layout(telemetry_panel, ratio=1),
        )

        footer = Panel(
            Text.from_markup(
                f"[dim]EVENT[/dim]  {self.last_event}"
                f"  [dim]|[/dim]  [dim]MODE[/dim]  {self.mode}"
                f"  [dim]|[/dim]  [dim]TARGET[/dim]  {self.message_count} messages"
            ),
            border_style="blue",
            padding=(0, 1),
        )

        body = Layout(name="body")
        body.split_row(
            Layout(progress_panel, ratio=2),
            right_column,
        )

        layout = Layout()
        layout.split_column(
            Layout(header, size=3),
            body,
            Layout(footer, size=3),
        )
        return layout

    def _elapsed(self) -> float:
        end_time = self.finished_at or time.monotonic()
        return max(0.0, end_time - self.started_at)

    def _send_rate(self) -> float:
        elapsed = self._elapsed()
        return self.sent_count / elapsed if elapsed > 0 else 0.0

    def _live_delivery_chart(self) -> Panel:
        bucket_count = 24
        bucket_width = 0.5
        elapsed = self._elapsed()
        current_bucket = int(elapsed / bucket_width)
        bucket_values = [0] * bucket_count

        for delivery_time in self.delivery_times:
            bucket = current_bucket - int(delivery_time / bucket_width)
            if 0 <= bucket < bucket_count:
                bucket_values[bucket_count - bucket - 1] += 1

        maximum = max(bucket_values, default=0)
        levels = " ▁▂▃▄▅▆▇█"
        chart = "".join(
            levels[
                min(
                    len(levels) - 1,
                    round(value / maximum * (len(levels) - 1)),
                )
            ]
            if maximum
            else levels[0]
            for value in bucket_values
        )

        return Panel(
            Text.from_markup(
                f"[bold green]{chart}[/bold green]\n"
                f"[dim]older[/dim] "
                f"[dim]each bar = {bucket_width:.1f}s[/dim] "
                f"[dim]now[/dim]"
            ),
            title=" LIVE DELIVERY PULSE ",
            title_align="left",
            border_style="green",
            padding=(0, 1),
        )

    def start(self) -> None:
        self.started_at = time.monotonic()
        self.live.start()

    def stop(self) -> None:
        self.finished_at = time.monotonic()
        self.live.stop()

    def advance(self) -> None:
        self.sent_count += 1
        self.delivery_times.append(time.monotonic() - self.started_at)
        self.last_event = "Message delivered"
        self.progress.advance(self.progress_task)
        self.live.update(self._render())

    def render_rate_limit(
        self,
        error: FloodWaitError,
        limit_count: int,
    ) -> None:
        self.limits_hit = limit_count
        self.last_event = (
            f"{error.scope.title()} limit; retry in {error.seconds}s"
        )
        self.status = Panel(
            f"[bold yellow]Rate limit #{limit_count}[/bold yellow]\n"
            f"Scope: [white]{error.scope}[/white]  "
            f"Retrying in [white]{error.seconds}s[/white]",
            title=" THROTTLED ",
            title_align="left",
            border_style="yellow",
            padding=(1, 2),
        )

        self.live.update(self._render())

    def render_summary(
        self,
        messages: list[Message],
        limits_hit: int,
    ) -> None:
        sent_messages = [
            message
            for message in messages
            if message.sent_at is not None
        ]
        wait_times = [
            message.wait_time
            for message in sent_messages
            if message.wait_time is not None
        ]

        total_wait_time = sum(wait_times)
        average_wait_time = (
            total_wait_time / len(wait_times)
            if wait_times
            else 0.0
        )
        duration = (
            max(message.sent_at for message in sent_messages)
            - min(message.created_at for message in sent_messages)
            if sent_messages
            else 0.0
        )
        throughput = (
            len(sent_messages) / duration
            if duration > 0
            else 0.0
        )
        maximum_wait = max(wait_times) if wait_times else 0.0

        summary = Table(
            title="SIMULATION COMPLETE",
            title_style="bold cyan",
            border_style="green",
            header_style="bold white",
            show_header=False,
            pad_edge=True,
            padding=(0, 2),
        )
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", justify="right", style="white")
        summary.add_row("Messages sent", str(len(wait_times)))
        summary.add_row("Rate limits hit", str(limits_hit))
        summary.add_row("Duration", f"{duration:.2f}s")
        summary.add_row("Throughput", f"{throughput:.2f} msg/s")
        summary.add_row("Total wait time", f"{total_wait_time:.2f}s")
        summary.add_row("Average wait time", f"{average_wait_time:.2f}s")
        summary.add_row("Maximum wait time", f"{maximum_wait:.2f}s")

        print(
            Panel(
                summary,
                title=" BROADCAST REPORT ",
                title_align="left",
                border_style="green",
                padding=(1, 2),
            )
        )
