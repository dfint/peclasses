from ctypes import Structure, sizeof
from typing import BinaryIO, Type, TypeVar, cast


def align(n, edge=4):
    return (n + edge - 1) & (-edge)


TStructure = TypeVar("TStructure", bound=Structure)


def read_structure(cls: Type[TStructure], file: BinaryIO, offset=None) -> TStructure:
    if offset is not None:
        file.seek(offset)

    raw = file.read(sizeof(cls))
    new_obj = cls.from_buffer_copy(raw)
    return new_obj


def write_structure(structure: TStructure, file: BinaryIO, offset=None) -> None:
    if offset is not None:
        file.seek(offset)

    file.write(cast(bytes, structure))
