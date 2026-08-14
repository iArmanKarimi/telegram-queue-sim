import plotext as plt

from models import Message


CHART_WIDTH = 100
CHART_HEIGHT = 25


def _prepare_chart(title: str, x_label: str, y_label: str) -> None:
    plt.clear_figure()
    plt.theme("pro")
    plt.plotsize(CHART_WIDTH, CHART_HEIGHT)

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)


def plot_wait_times(messages: list[Message]) -> None:
    sent_messages = [
        message
        for message in messages
        if message.wait_time is not None
    ]

    message_indices = [message.index for message in sent_messages]
    wait_times = [message.wait_time for message in sent_messages]

    _prepare_chart(
        title="Message Wait Time",
        x_label="Message",
        y_label="Seconds",
    )

    plt.scatter(message_indices, wait_times)
    plt.show()


def plot_wait_times_by_chat(messages: list[Message]) -> None:
    sent_messages = [
        message
        for message in messages
        if message.wait_time is not None
    ]

    chat_ids = [message.chat_id for message in sent_messages]
    wait_times = [message.wait_time for message in sent_messages]

    _prepare_chart(
        title="Message Wait Time by Chat",
        x_label="Chat",
        y_label="Seconds",
    )

    plt.scatter(chat_ids, wait_times)
    plt.show()


def plot_average_wait_by_chat(messages: list[Message]) -> None:
    chat_waits: dict[int, list[float]] = {}

    for message in messages:
        if message.wait_time is None:
            continue

        chat_waits.setdefault(message.chat_id, []).append(message.wait_time)

    chat_ids = sorted(chat_waits)
    average_waits = [
        sum(wait_times) / len(wait_times)
        for wait_times in (chat_waits[chat_id] for chat_id in chat_ids)
    ]

    _prepare_chart(
        title="Average Wait Time by Chat",
        x_label="Chat",
        y_label="Seconds",
    )

    plt.bar(chat_ids, average_waits)
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

    plt.show()


def plot_wait_time_distribution(messages: list[Message]) -> None:
    wait_times = [
        message.wait_time
        for message in messages
        if message.wait_time is not None
    ]

    _prepare_chart(
        title="Wait Time Distribution",
        x_label="Wait (seconds)",
        y_label="Messages",
    )

    plt.hist(wait_times)
    plt.show()


def analyze(messages: list[Message]) -> None:
    plot_wait_time_distribution(messages)
    plot_wait_time_by_chat(messages)
    plot_average_wait_by_chat(messages)
    plot_message_timeline(messages)
    plot_wait_time_distribution(messages)
