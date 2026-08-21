import argparse

from rich import print
from rich.panel import Panel

from analyze import analyze
from bot import Bot
from render import Renderer
from simulator import MessageSimulator


MESSAGE_COUNT = 50


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
    args = parser.parse_args()

    if args.messages < 0:
        parser.error("--messages must be zero or greater")

    return args


def main() -> None:
    args = parse_args()

    print(
        Panel.fit(
            "[bold cyan]"
            "🔬 TELEGRAM: MESSAGE BROADCAST (RATE LIMIT SIMULATOR) 🔬"
            "[/bold cyan]",
            border_style="cyan",
        )
    )

    renderer = Renderer(args.messages)

    bot = Bot(
        on_message_sent=renderer.advance,
        on_rate_limit=renderer.render_rate_limit,
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

    analyze(messages, show_plots=not args.no_plots)


if __name__ == "__main__":
    main()
