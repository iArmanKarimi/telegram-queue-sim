import argparse

from rich import print
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from analyze import analyze
from bot import Bot
from render import Renderer
from simulator import MessageSimulator


MESSAGE_COUNT = 50


def render_banner(message_count: int, use_queue: bool) -> Panel:
    mode = "QUEUE-AWARE SCHEDULER" if use_queue else "NAIVE FIFO SENDER"
    mode_style = "green" if use_queue else "yellow"

    banner = Table.grid(padding=(0, 2), expand=False)
    banner.add_row(
        Text("TELEGRAM", style="bold cyan"),
        Text("QUEUE SIM", style="bold white"),
    )
    banner.add_row(
        Text("RATE-LIMITED BROADCAST LAB", style="bold yellow"),
    )
    banner.add_row(Text(mode, style=f"bold {mode_style}"))
    banner.add_row(
        Text("30 msg/s global", style="dim"),
        Text("1 msg/s per chat", style="dim"),
        Text(f"{message_count} messages", style="dim"),
    )

    return Panel(
        Align.center(banner),
        title=" BROADCAST CONTROL ROOM ",
        title_align="left",
        subtitle="[dim]simulated delivery telemetry[/dim]",
        subtitle_align="right",
        border_style="cyan",
        padding=(1, 3),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulate Telegram-style rate-limited message delivery.",
    )
    parser.add_argument(
        "-n",
        "--messages",
        type=int,
        default=MESSAGE_COUNT,
        help=f"number of messages to send (default: {MESSAGE_COUNT})",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="skip the interactive analysis charts",
    )
    parser.add_argument(
        "--naive",
        action="store_true",
        help="use a blocking FIFO sender instead of the queue scheduler",
    )
    args = parser.parse_args()

    if args.messages < 0:
        parser.error("--messages must be zero or greater")

    return args


def main() -> None:
    args = parse_args()

    use_queue = not args.naive
    print(render_banner(args.messages, use_queue))

    renderer = Renderer(
        args.messages,
        mode="QUEUE-AWARE" if use_queue else "NAIVE FIFO",
    )

    bot = Bot(
        on_message_sent=renderer.advance,
        on_rate_limit=renderer.render_rate_limit,
        use_queue=use_queue,
    )

    simulator = MessageSimulator(bot)

    renderer.start()

    try:
        messages = simulator.run(args.messages)
    finally:
        renderer.stop()

    renderer.render_summary(
        messages=messages,
        limits_hit=bot.limits_hit,
    )

    analyze(
        messages,
        show_plots=not args.no_plots,
        show_summary=False,
    )


if __name__ == "__main__":
    main()
