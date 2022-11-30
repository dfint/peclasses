from ctypes import c_uint
from typing import BinaryIO, Iterator, Optional, Sequence, cast

from peclasses.bisect_helper import Bisector
from peclasses.pe_classes import ImageSectionHeader
from peclasses.type_aliases import Offset, Rva
from peclasses.utilities import read_structure


class Section(ImageSectionHeader):
    def __init__(
        self,
        name: bytes,
        characteristics: int,
        pointer_to_raw_data: int,
        size_of_raw_data: int,
        virtual_address: int,
        virtual_size: int,
    ):
        super().__init__()
        self.name = type(self.name)(name)
        self.characteristics = c_uint(characteristics)
        self.pointer_to_raw_data = c_uint(pointer_to_raw_data)
        self.size_of_raw_data = c_uint(size_of_raw_data)
        self.virtual_address = c_uint(virtual_address)
        self.virtual_size = c_uint(virtual_size)

    def offset_to_rva(self, offset: Offset) -> Rva:
        """
        Converts given physical offset within current section to a rva
        """
        local_offset = offset - cast(int, self.pointer_to_raw_data)
        assert 0 <= local_offset < cast(int, self.size_of_raw_data)
        return local_offset + cast(int, self.virtual_address)

    def rva_to_offset(self, virtual_address: Rva) -> Offset:
        """
        Converts given rva within current section to a physical offset
        """
        local_offset = virtual_address - cast(int, self.virtual_address)
        assert 0 <= local_offset < self.virtual_size
        return local_offset + cast(int, self.pointer_to_raw_data)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.name!r}, flags=0x{self.characteristics:X}, "
            f"pstart=0x{self.pointer_to_raw_data:X}, psize=0x{self.size_of_raw_data:X}, "
            f"vstart=0x{self.virtual_address:X}, vsize=0x{self.virtual_size:X})"
        )


class SectionTable(Sequence[Section]):
    _sections: Sequence[Section]
    _offset_bisector: Bisector[Section]
    _rva_bisector: Bisector[Section]

    def __init__(self, sections: Sequence[Section]):
        self._sections = sections

        # Make auxiliary objects to perform bisection search among physical offsets and rvas:
        self._offset_bisector = Bisector(self._sections, lambda x: cast(int, x.pointer_to_raw_data))
        self._rva_bisector = Bisector(self._sections, lambda x: cast(int, x.virtual_address))

        assert all(x.virtual_address < self._sections[i + 1].virtual_address for i, x in enumerate(self._sections[:-1]))
        assert all(x.pointer_to_raw_data < self._sections[i + 1].pointer_to_raw_data for i, x in enumerate(self[:-1]))

    @classmethod
    def read(cls, file: BinaryIO, offset: Offset, number: int) -> "SectionTable":
        """
        Initialize a SectionTable from a file object
        """
        file.seek(offset)
        return cls([read_structure(Section, file) for _ in range(number)])

    def write(self, file: BinaryIO, offset: Optional[Offset] = None) -> None:
        """
        Write the SectionTable to a file object
        """
        if offset is not None:
            file.seek(offset)

        for section in self._sections:
            file.write(cast(bytes, section))

    def offset_to_rva(self, offset: Offset) -> Rva:
        """
        Converts given physical offset to rva
        """
        section = self.which_section(offset=offset)
        return section.offset_to_rva(offset)

    def rva_to_offset(self, rva: Rva) -> Offset:
        """
        Converts given rva to physical offset
        """
        section = self.which_section(rva=rva)
        return section.rva_to_offset(rva)

    def which_section(self, offset: Optional[Offset] = None, rva: Optional[Rva] = None) -> Section:
        """
        Returns a section to which belongs given offset or rva
        """
        return self._sections[self.which_section_index(offset, rva)]

    def which_section_index(self, offset: Optional[Offset] = None, rva: Optional[Rva] = None) -> int:
        """
        Returns a section index to which belongs given offset or rva
        """
        if offset is not None:
            return self._offset_bisector.bisect(offset) - 1
        elif rva is not None:
            return self._rva_bisector.bisect(rva) - 1
        else:
            raise ValueError("One of arguments (offset or rva) must be filled")

    def __getitem__(self, item):
        return self._sections[item]

    def __len__(self) -> int:
        return len(self._sections)

    def __iter__(self) -> Iterator[Section]:
        return iter(self._sections)

    def __repr__(self) -> str:
        return "SectionTable([\n\t{}\n])".format(",\n\t".join(repr(x) for x in self._sections))
