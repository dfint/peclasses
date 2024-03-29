from ctypes import sizeof
from typing import BinaryIO, Optional, SupportsBytes, Union, cast

from peclasses.pe_classes import (
    ImageDataDirectory,
    ImageDataDirectoryArray,
    ImageDosHeader,
    ImageFileHeader,
    ImageNTHeaders,
    ImageNTHeaders64,
    ImageOptionalHeader,
    ImageOptionalHeader64,
    OptionalHeaderVersionMagic,
)
from peclasses.relocation_table import RelocationTable
from peclasses.section_table import Section, SectionTable
from peclasses.type_aliases import Offset
from peclasses.utilities import align, read_structure, write_structure


class PortableExecutable:
    file: BinaryIO
    dos_header: ImageDosHeader
    nt_headers: Union[ImageNTHeaders, ImageNTHeaders64]
    file_header: ImageFileHeader
    optional_header: Union[ImageOptionalHeader, ImageOptionalHeader64]
    data_directory: ImageDataDirectoryArray
    _section_table: Optional[SectionTable]
    _relocation_table: Optional[RelocationTable]

    def __init__(self, file: BinaryIO):
        self._read_file(file)

    def _read_file(self, file: BinaryIO) -> None:
        self.file = file
        self.file.seek(0)
        self.dos_header = read_structure(ImageDosHeader, file)
        assert self.dos_header.e_magic == b"MZ"

        file.seek(cast(int, self.dos_header.e_lfanew))
        nt_headers_signature = file.read(4)
        assert nt_headers_signature == b"PE\0\0"

        file.seek(self.optional_header_offset)
        optional_header_magic = int.from_bytes(file.read(2), "little")
        nt_headers_offset = cast(int, self.dos_header.e_lfanew)

        if optional_header_magic == OptionalHeaderVersionMagic.IMAGE_NT_OPTIONAL_HDR32_MAGIC:
            self.nt_headers = read_structure(ImageNTHeaders, file, nt_headers_offset)
        elif optional_header_magic == OptionalHeaderVersionMagic.IMAGE_NT_OPTIONAL_HDR64_MAGIC:
            self.nt_headers = read_structure(ImageNTHeaders64, file, nt_headers_offset)
        else:
            raise ValueError(f"Optional header magic 0x{optional_header_magic:X} is not supported")

        self.file_header = self.nt_headers.file_header
        self.optional_header = self.nt_headers.optional_header
        self.data_directory = self.optional_header.data_directory
        self._section_table = None
        self._relocation_table = None

    def reread(self) -> None:
        self._read_file(self.file)

    @property
    def optional_header_offset(self) -> Offset:
        return cast(int, self.dos_header.e_lfanew) + 4 + sizeof(ImageFileHeader)

    def rewrite_nt_headers(self) -> None:
        offset = self.dos_header.e_lfanew
        nt_headers_data = bytes(cast(SupportsBytes, self.nt_headers))[: self.nt_headers_size]
        self.file.seek(cast(int, offset))
        self.file.write(nt_headers_data)

    def rewrite_data_directory(self) -> None:
        data_directory_data = bytes(cast(SupportsBytes, self.data_directory))[: self.data_directory_size]
        self.file.seek(self.data_directory_offset)
        self.file.write(data_directory_data)

    @property
    def data_directory_offset(self) -> Offset:
        return cast(int, self.dos_header.e_lfanew) + sizeof(self.nt_headers) - sizeof(ImageDataDirectoryArray)

    @property
    def data_directory_size(self) -> int:
        return sizeof(ImageDataDirectory) * cast(int, self.optional_header.number_of_rva_and_sizes)

    @property
    def nt_headers_size(self) -> int:
        # Real size of the optional_header depends on number_of_rva_and_sizes value
        return sizeof(self.nt_headers) - sizeof(ImageDataDirectoryArray) + self.data_directory_size

    @property
    def section_table_offset(self) -> Offset:
        return cast(int, self.dos_header.e_lfanew) + self.nt_headers_size

    @property
    def section_table(self) -> SectionTable:
        if self._section_table is None:
            n = cast(int, self.file_header.number_of_sections)
            offset = self.section_table_offset
            self._section_table = SectionTable.read(self.file, offset, n)
        return self._section_table

    @property
    def relocation_table(self) -> RelocationTable:
        if self._relocation_table is None:
            rva = cast(int, self.data_directory.basereloc.virtual_address)
            offset = self.section_table.rva_to_offset(rva)
            size = cast(int, self.data_directory.basereloc.size)
            self.file.seek(offset)
            self._relocation_table = RelocationTable.from_file(self.file, size)
        return self._relocation_table

    def add_new_section(self, new_section: Section, data_size: int) -> None:
        file = self.file
        sections = self.section_table
        section_alignment = cast(int, self.optional_header.section_alignment)
        file_alignment = cast(int, self.optional_header.file_alignment)
        file_size = align(cast(int, new_section.pointer_to_raw_data) + data_size, file_alignment)
        new_section.size_of_raw_data = file_size - cast(int, new_section.pointer_to_raw_data)

        # Align file size
        file.truncate(file_size)

        # Set the new section virtual size
        new_section.virtual_size = data_size

        # Write the new section info
        write_structure(new_section, file, self.section_table_offset + len(sections) * sizeof(Section))

        # Fix number of sections
        self.file_header.number_of_sections = len(sections) + 1
        # Fix ImageSize field of the PE header
        self.optional_header.size_of_image = align(
            cast(int, new_section.virtual_address) + new_section.virtual_size, section_alignment
        )
        self.rewrite_nt_headers()
