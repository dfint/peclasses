import bisect
from typing import Sequence, Callable, TypeVar, Generic

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


class Bisector(Generic[TValue]):
    _wrapper: KeySequenceWrapper[TValue]

    def __init__(self, sequence: Sequence[TValue], key: Callable[[TValue], int]):
        self._wrapper = KeySequenceWrapper(sequence, key)

    def bisect_right(self, x: int, *args, **kwargs) -> int:
        return bisect.bisect_right(self._wrapper, x, *args, **kwargs)

    bisect = bisect_right

    def bisect_left(self, x: int, *args, **kwargs) -> int:
        return bisect.bisect_left(self._wrapper, x, *args, **kwargs)
