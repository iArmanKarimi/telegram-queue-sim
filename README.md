# Telegram Queue Sim

A CLI runnable simulation of **per-chat rate-limited message queuing** for a
Telegram bot — a case study in dealing with Telegram's 1 msg/s per-chat limit.

## Why

Telegram allows ~30 messages/sec per bot token, but only **1 message/sec per
chat**. A naive "sleep after every send" queue throttles all chats equally and
wastes capacity. This project simulates the arrivals and demonstrates a
per-chat cooldown instead.

## What you'll see

- Simulated messages arriving at a chat at random intervals
- A queue that buffers messages that exceed the 1 msg/s limit
- Visualized output showing arrival vs. sent times (and the wait)

## Usage

```bash
python main.py
```
