from enum import Enum


class ReviewStateEnum(Enum):

    PENDING = 'pending'
    PROGRESS = 'progress'
    COMPLETED = 'completed'

    def __str__(self) -> str:
        return self.value
