import shutil

import plotext as plt

from models import Message


def _chart_size() -> tuple[int, int]:
    terminal = shutil.get_terminal_size((100, 30))
    width = max(48, min(100, terminal.columns - 4))
    height = max(12, min(22, terminal.lines - 8))
    return width, height


def _prepare_chart(
    title: str,
    x_label: str,
    y_label: str,
) -> None:
    plt.clear_figure()
    plt.theme("pro")
    width, height = _chart_size()
    plt.plotsize(width, height)

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)


def plot_wait_times(messages: list[Message]) -> None:
    sent_messages = [
        message
        for message in messages
        if message.wait_time is not None
    ]

    if not sent_messages:
        return

    message_indices = [
        message.index
        for message in sent_messages
    ]

    wait_times = [
        message.wait_time
        for message in sent_messages
    ]

    _prepare_chart(
        title="Message Wait Time",
        x_label="Message",
        y_label="Seconds",
    )

    plt.scatter(message_indices, wait_times)
    plt.xfrequency(max(1, len(message_indices) // 8))
    plt.show()


def plot_average_wait_by_chat(messages: list[Message]) -> None:
    chat_waits: dict[int, list[float]] = {}

    for message in messages:
        if message.wait_time is None:
            continue

        chat_waits.setdefault(message.chat_id, []).append(
            message.wait_time
        )

    if not chat_waits:
        return

    chat_ids = sorted(chat_waits)

    average_waits = [
        sum(chat_waits[chat_id]) / len(chat_waits[chat_id])
        for chat_id in chat_ids
    ]

    _prepare_chart(
        title="Average Wait Time by Chat",
        x_label="Chat",
        y_label="Seconds",
    )

    plt.bar(chat_ids, average_waits)
    plt.xfrequency(1)
    plt.show()


def plot_message_timeline(messages: list[Message]) -> None:
    sent_messages = [
        message
        for message in messages
        if message.sent_at is not None
    ]

    if not sent_messages:
        return

    start_time = min(
        message.created_at
        for message in sent_messages
    )

    _prepare_chart(
        title="Message Timeline",
        x_label="Time (seconds)",
        y_label="Message",
    )

    for message in sent_messages:
        arrival_time = message.created_at - start_time
        sent_time = message.sent_at - start_time

        plt.plot(
            [arrival_time, sent_time],
            [message.index, message.index],
            marker="dot",
        )

    plt.yfrequency(max(1, len(sent_messages) // 8))
    plt.show()


def print_summary(messages: list[Message]) -> None:
    sent_messages = [
        message
        for message in messages
        if message.sent_at is not None
    ]

    if not sent_messages:
        return

    wait_times = [
        message.wait_time
        for message in sent_messages
        if message.wait_time is not None
    ]

    start_time = min(
        message.created_at
        for message in sent_messages
    )

    end_time = max(
        message.sent_at
        for message in sent_messages
    )

    duration = end_time - start_time
    throughput = len(sent_messages) / duration if duration > 0 else 0.0
    average_wait = (
        sum(wait_times) / len(wait_times)
        if wait_times
        else 0.0
    )

    print(
        f"\nMessages: {len(sent_messages)}"
        f"\nDuration: {duration:.2f}s"
        f"\nThroughput: {throughput:.2f} msg/s"
        f"\nAverage wait: {average_wait:.2f}s"
        f"\nMaximum wait: {max(wait_times):.2f}s"
    )


def analyze(
    messages: list[Message],
    show_plots: bool = True,
    show_summary: bool = True,
) -> None:
    if show_summary:
        print_summary(messages)

    if not show_plots:
        return

    plot_wait_times(messages)
    plot_average_wait_by_chat(messages)
    plot_message_timeline(messages)
