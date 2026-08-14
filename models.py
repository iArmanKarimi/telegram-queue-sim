from dataclasses import dataclass


@dataclass
class Message:
    index: int
    chat_id: int
    created_at: float
    sent_at: float | None = None

    @property
    def wait_time(self) -> float | None:
        if self.sent_at is None:
            return None

        return self.sent_at - self.created_at