import bisect
from array import array
from typing import BinaryIO, Iterable, List, Mapping, MutableMapping, Tuple, Iterator

from peclasses.utilities import align


class RelocationTable:
    IMAGE_REL_BASED_ABSOLUTE = 0
    IMAGE_REL_BASED_HIGHLOW = 3

    _table: Mapping[int, List[int]]

    def __init__(self, table: Mapping[int, List[int]]):
        self._table = table

    def __iter__(self) -> Iterator[int]:
        for page, records in self._table.items():
            for record in records:
                yield page | (record & 0x0FFF)

    @classmethod
    def build(cls, relocs: Iterable[int]) -> "RelocationTable":
        reloc_table: MutableMapping[int, List[int]] = dict()
        for item in relocs:
            page = item & 0xFFFFF000
            offset = item & 0x00000FFF
            if page not in reloc_table:
                reloc_table[page] = []
            bisect.insort(reloc_table[page], offset)
        return cls(reloc_table)

    @staticmethod
    def iter_read(file: BinaryIO, reloc_size: int) -> Iterable[Tuple[int, List[int]]]:
        cur_off = 0
        while cur_off < reloc_size:
            cur_page = int.from_bytes(file.read(4), "little")
            block_size = int.from_bytes(file.read(4), "little")
            assert block_size > 8, block_size
            assert (block_size - 8) % 2 == 0
            relocs = array("H")
            relocs.fromfile(file, (block_size - 8) // 2)
            yield cur_page, [x for x in relocs if x >> 12 == RelocationTable.IMAGE_REL_BASED_HIGHLOW]
            cur_off += block_size

    @classmethod
    def from_file(cls, file: BinaryIO, reloc_size: int) -> "RelocationTable":
        return cls(dict(cls.iter_read(file, reloc_size)))

    @property
    def size(self) -> int:
        words = sum(align(len(val), 2) for val in self._table.values())
        return len(self._table) * 8 + words * 2

    def to_file(self, file: BinaryIO) -> None:
        for page in sorted(self._table):
            records = [item | RelocationTable.IMAGE_REL_BASED_HIGHLOW << 12 for item in self._table[page]]

            # Padding records:
            if len(records) % 2 == 1:
                records.append(RelocationTable.IMAGE_REL_BASED_ABSOLUTE << 12 | 0)
            block_size = 8 + 2 * len(records)  # 2 dwords + N words
            array("I", [page, block_size]).tofile(file)
            array("H", records).tofile(file)
