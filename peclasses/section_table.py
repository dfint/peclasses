import bisect
from ctypes import c_uint
from itertools import zip_longest
from typing import Sequence, SupportsBytes, Callable, Type, Iterable

from peclasses.pe_classes import ImageSectionHeader
from peclasses.type_aliases import Offset, Rva
from peclasses.utilities import read_structure

K = Type["K"]
V = Type["V"]


class KeySequenceWrapper(Sequence):
    sequence: Sequence[V]
    key: Callable[[K], V]

    def __init__(self, sequence: Sequence[V], key: Callable[[K], V]):
        self.sequence = sequence
        self.key = key

    def __len__(self) -> int:
        return len(self.sequence)

    def __getitem__(self, i: K) -> V:
        return self.key(self.sequence[i])


class Section(ImageSectionHeader):
    def __init__(
            self,
            name: bytes,
            flags: int,
            pointer_to_raw_data: int,
            size_of_raw_data: int,
            virtual_address: int,
            virtual_size: int
    ):
        super().__init__()
        self.name = type(self.name)(name)
        self.characteristics = c_uint(flags)
        self.pointer_to_raw_data = c_uint(pointer_to_raw_data)
        self.size_of_raw_data = c_uint(size_of_raw_data)
        self.virtual_address = c_uint(virtual_address)
        self.virtual_size = c_uint(virtual_size)

    def offset_to_rva(self, offset: Offset) -> Rva:
        local_offset = offset - self.pointer_to_raw_data
        assert 0 <= local_offset < self.size_of_raw_data
        return local_offset + self.virtual_address

    def rva_to_offset(self, virtual_address: Rva):
        local_offset = virtual_address - self.virtual_address
        assert 0 <= local_offset < self.virtual_size
        return local_offset + self.pointer_to_raw_data

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.name!r}, flags=0x{self.characteristics:X}, "
            f"pstart=0x{self.pointer_to_raw_data:X}, psize=0x{self.size_of_raw_data:X}, "
            f"vstart=0x{self.virtual_address:X}, vsize=0x{self.virtual_size:X})"
        )


class SectionTable(Sequence[Section]):
    def __init__(self, sections: Sequence[Section]):
        self._sections: Sequence[Section] = sections

        # Make auxiliary objects to perform bisection search among physical offsets and rvas:
        self._offset_key = KeySequenceWrapper(self, lambda x: x.pointer_to_raw_data)
        self._rva_key = KeySequenceWrapper(self, lambda x: x.virtual_address)

        assert all(x.virtual_address < self._sections[i + 1].virtual_address
                   for i, x in enumerate(self._sections[:-1]))
        assert all(x.pointer_to_raw_data < self._sections[i + 1].pointer_to_raw_data
                   for i, x in enumerate(self[:-1]))

    @classmethod
    def read(cls, file, offset, number) -> "SectionTable":
        file.seek(offset)
        return cls([read_structure(Section, file) for _ in range(number)])

    def write(self, file, offset=None) -> None:
        if offset is not None:
            file.seek(offset)

        section: SupportsBytes
        for section in self._sections:
            file.write(bytes(section))

    def offset_to_rva(self, offset: Offset) -> Rva:
        i = bisect.bisect(self._offset_key, offset) - 1
        return self._sections[i].offset_to_rva(offset)

    def rva_to_offset(self, rva: Rva) -> Offset:
        i = bisect.bisect(self._rva_key, rva) - 1
        return self._sections[i].rva_to_offset(rva)

    def which_section(self, offset: Offset = None, rva: Rva = None):
        if offset is not None:
            return bisect.bisect(self._offset_key, offset) - 1
        elif rva is not None:
            return bisect.bisect(self._rva_key, rva) - 1
        else:
            raise ValueError("One of arguments (offset or rva) must be filled")

    def diff(self, other):
        for left, right in zip_longest(self._sections, other):
            if left != right:
                yield left, right

    def __repr__(self) -> str:
        return "SectionTable([\n\t{}\n])".format(",\n\t".join(repr(x) for x in self._sections))

    def __str__(self) -> str:
        return "SectionTable([\n\t{}\n])".format(",\n\t".join(str(x) for x in self._sections))

    def __getitem__(self, item):
        return self._sections[item]

    def __len__(self) -> int:
        return len(self._sections)

    def __iter__(self) -> Iterable[Section]:
        return iter(self._sections)
