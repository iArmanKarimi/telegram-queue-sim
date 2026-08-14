from rich import print
from rich.panel import Panel

from bot import Bot
from render import Renderer
from simulator import MessageSimulator


MESSAGE_COUNT = 50


def main() -> None:
    print(
        Panel.fit(
            "[bold cyan]"
            "🔬 TELEGRAM: MESSAGE BROADCAST (RATE LIMIT SIMULATOR) 🔬"
            "[/bold cyan]",
            border_style="cyan",
        )
    )

    renderer = Renderer(MESSAGE_COUNT)

    bot = Bot(
        on_rate_limit=renderer.render_rate_limit,
    )

    simulator = MessageSimulator(
        bot=bot,
        on_message_sent=renderer.advance,
    )

    renderer.start()

    try:
        messages = simulator.run(MESSAGE_COUNT)
    finally:
        renderer.stop()

    renderer.render_summary(
        messages=messages,
        limits_hit=bot.limits_hit,
    )


if __name__ == "__main__":
    main()