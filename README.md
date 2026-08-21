# Telegram Queue Sim

A CLI simulation of **rate-limited message delivery for a Telegram bot**.

The project models Telegram's approximate bot-wide broadcast limit and
per-chat message-rate restriction, then explores how a queue can handle
rate-limited messages without unnecessarily blocking other chats.

## Why

A naive approach can react to a rate-limit error by sleeping before trying
again. When messages for multiple chats share the same sending loop, this can
unnecessarily delay messages that could still be delivered.

This project demonstrates that approach with a **per-chat-aware message
queue**. Messages for chats that are ready can continue while another chat is
waiting for its rate limit to expire.

## Current model

The simulated API uses:

- **30 messages/sec** bot-wide
- **1 message/sec** per chat
- A `FloodWaitError` when a limit is exceeded
- Five randomly selected chats for generated messages

These are simplified rules for the simulation and are not intended to be an
exact implementation of Telegram's internal rate-limiting behavior.

## Setup

The project requires Python 3.10 or newer and the packages listed in
`requirements.txt`.

```bash
python -m venv .venv
```

Activate the virtual environment, then install the dependencies:

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Usage

Run the default simulation with 50 messages:

```bash
python main.py
```

Change the number of messages with `--messages` or `-n`:

```bash
python main.py --messages 100
python main.py -n 10
```

Use `--no-plots` to skip the interactive charts in a headless terminal or in
automation:

```bash
python main.py --messages 10 --no-plots
```

To compare the queue-aware scheduler with a naive blocking sender, add
`--naive`:

```bash
python main.py --messages 50 --naive --no-plots
```

The default queue-aware mode tracks global and per-chat availability and
selects another ready chat when one chat is throttled. Naive mode sends in
FIFO order and sleeps on a `FloodWaitError`, so one limited chat blocks every
message behind it. Compare the `Rate limits hit`, `Average wait time`, and
`Throughput` values in the broadcast reports. Because arrivals and chat
assignments are random, use larger runs or repeat each mode when comparing
results.

The complete option list is available with:

```bash
python main.py --help
```

The normal run displays live progress and a completion summary, then shows:

- Wait time for each message
- Average wait time by chat
- A message arrival-to-delivery timeline

## How It Works

1. `MessageSimulator` creates messages for random chats and enqueues them at
	short, random intervals.
2. `Bot` runs a sender thread and tracks the next available time globally and
	for each chat.
3. `MessageQueue` scans for any ready message instead of blocking on the
	first queued message.
4. `TelegramAPI` applies the simulated limits and raises `FloodWaitError`
	when a send is rejected.
5. `analyze.py` calculates wait-time metrics and renders charts with
	`plotext`.

## Project Files

| File | Responsibility |
| --- | --- |
| `main.py` | CLI entry point and simulation orchestration |
| `simulator.py` | Generates messages and simulates arrivals |
| `bot.py` | Background sender and global/per-chat scheduling |
| `message_queue.py` | Thread-safe queue of pending messages |
| `api.py` | Simulated Telegram API and flood-wait errors |
| `models.py` | Message data model and wait-time calculation |
| `render.py` | Live progress display and summary panel |
| `analyze.py` | Metrics and terminal charts |

## Limitations

This is a deterministic queueing demonstration only in terms of its rules;
message order and arrival timing are randomized on each run. It does not call
Telegram, persist messages, retry failed processes after shutdown, or model
all Telegram API limits. The simulated limits should not be used as production
configuration.
