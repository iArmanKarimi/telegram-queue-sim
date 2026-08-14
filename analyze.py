import plotext as plt

from models import Message


CHART_WIDTH = 100
CHART_HEIGHT = 25


def plot_wait_times(messages: list[Message]) -> None:
    message_indices = []
    wait_times = []

    for message in messages:
        if message.wait_time is None:
            continue

        message_indices.append(message.index)
        wait_times.append(message.wait_time)

    plt.clear_figure()
    plt.theme("pro")
    plt.plotsize(CHART_WIDTH, CHART_HEIGHT)

    plt.title("Message Wait Time")
    plt.xlabel("Message")
    plt.ylabel("Seconds")

    plt.scatter(message_indices, wait_times)

    plt.show()


def plot_wait_times_by_chat(messages: list[Message]) -> None:
    chat_ids = []
    wait_times = []

    for message in messages:
        if message.wait_time is None:
            continue

        chat_ids.append(message.chat_id)
        wait_times.append(message.wait_time)

    plt.clear_figure()
    plt.theme("pro")
    plt.plotsize(CHART_WIDTH, CHART_HEIGHT)

    plt.title("Message Wait Time by Chat")
    plt.xlabel("Chat")
    plt.ylabel("Seconds")

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
        sum(chat_waits[chat_id]) / len(chat_waits[chat_id])
        for chat_id in chat_ids
    ]

    plt.clear_figure()
    plt.theme("pro")
    plt.plotsize(CHART_WIDTH, CHART_HEIGHT)

    plt.title("Average Wait Time by Chat")
    plt.xlabel("Chat")
    plt.ylabel("Seconds")

    plt.bar(chat_ids, average_waits)

    plt.show()


def analyze(messages: list[Message]) -> None:
    plot_wait_times(messages)
    plot_wait_times_by_chat(messages)
    plot_average_wait_by_chat(messages)
