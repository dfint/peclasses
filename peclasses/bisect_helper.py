from typing import Sequence, Callable, TypeVar

TValue = TypeVar("TValue")


class KeySequenceWrapper(Sequence[TValue]):
    sequence: Sequence[TValue]
    key: Callable[[TValue], int]

    def __init__(self, sequence: Sequence[TValue], key: Callable[[TValue], int]):
        self.sequence = sequence
        self.key = key

    def __len__(self) -> int:
        return len(self.sequence)

    def __getitem__(self, i: int) -> int:
        return self.key(self.sequence[i])
