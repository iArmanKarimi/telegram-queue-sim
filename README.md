# Telegram Queue Sim

A CLI simulation of **rate-limited message delivery for a Telegram bot**.

The project models Telegram's approximate bot-wide broadcast limit and
per-chat message-rate restriction, then explores how a queue can handle
rate-limited messages without unnecessarily blocking other chats.

## Why

A naive approach can react to a rate-limit error by sleeping before trying
again. When messages for multiple chats share the same sending loop, this can
unnecessarily delay messages that could still be delivered.

This project simulates that problem and builds toward a **per-chat-aware
message queue**.

## Current model

The simulated API uses:

- **~30 messages/sec** bot-wide
- **~1 message/sec** per chat
- A `FloodWaitError` when a limit is exceeded

These are simplified rules for the simulation and are not intended to be an
exact implementation of Telegram's internal rate-limiting behavior.

## Usage

```bash
python main.py
