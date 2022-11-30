import bisect
import sys
from typing import Sequence, Callable, TypeVar, Generic

TValue = TypeVar("TValue")


if sys.version_info[0:2] >= (3, 10):
    class Bisector(Generic[TValue]):
        _sequence: Sequence[TValue]
        _key: Callable[[TValue], int]

        def __init__(self, sequence: Sequence[TValue], key: Callable[[TValue], int]):
            self._sequence = sequence
            self._key = key

        def bisect_right(self, x: int) -> int:
            return bisect.bisect_right(self._sequence, x, key=self._key)

        bisect = bisect_right

        def bisect_left(self, x: int) -> int:
            return bisect.bisect_left(self._sequence, x, key=self._key)
else:
    class _KeySequenceWrapper(Sequence[TValue]):
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
        _wrapper: _KeySequenceWrapper[TValue]

        def __init__(self, sequence: Sequence[TValue], key: Callable[[TValue], int]):
            self._wrapper = _KeySequenceWrapper(sequence, key)

        def bisect_right(self, x: int) -> int:
            return bisect.bisect_right(self._wrapper, x)

        bisect = bisect_right

        def bisect_left(self, x: int) -> int:
            return bisect.bisect_left(self._wrapper, x)
