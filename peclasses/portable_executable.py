from ctypes import sizeof
from typing import BinaryIO, Optional, Union

from peclasses.pe_classes import (
    ImageDosHeader, ImageNTHeaders, ImageFileHeader, ImageOptionalHeader, ImageDataDirectoryArray,
    ImageOptionalHeader64,
    ImageNTHeaders64, OptionalHeaderVersionMagic, ImageDataDirectory
)
from peclasses.relocation_table import RelocationTable
from peclasses.section_table import SectionTable, Section
from peclasses.type_aliases import Offset
from peclasses.utilities import read_structure, write_structure, align


class PortableExecutable:
    file: BinaryIO
    dos_header: ImageDosHeader
    nt_headers: Union[ImageNTHeaders, ImageNTHeaders64]
    file_header: ImageFileHeader
    optional_header: Union[ImageOptionalHeader, ImageOptionalHeader64]
    data_directory: ImageDataDirectoryArray
    _section_table: Optional[SectionTable]
    _relocation_table: Optional[RelocationTable]

    def __init__(self, file):
        self._read_file(file)

    def _read_file(self, file):
        self.file = file
        self.file.seek(0)
        self.dos_header = read_structure(ImageDosHeader, file)
        assert self.dos_header.e_magic == b"MZ"

        file.seek(self.dos_header.e_lfanew)
        nt_headers_signature = file.read(4)
        assert nt_headers_signature == b"PE\0\0"

        file.seek(self.optional_header_offset)
        optional_header_magic = int.from_bytes(file.read(2), 'little')

        if optional_header_magic == OptionalHeaderVersionMagic.IMAGE_NT_OPTIONAL_HDR32_MAGIC:
            self.nt_headers = read_structure(ImageNTHeaders, file, self.dos_header.e_lfanew)
        elif optional_header_magic == OptionalHeaderVersionMagic.IMAGE_NT_OPTIONAL_HDR64_MAGIC:
            self.nt_headers = read_structure(ImageNTHeaders64, file, self.dos_header.e_lfanew)
        else:
            raise ValueError(f"Optional header magic 0x{optional_header_magic:X} is not supported")

        self.file_header = self.nt_headers.file_header
        self.optional_header = self.nt_headers.optional_header
        self.data_directory = self.optional_header.image_data_directory
        self._section_table = None
        self._relocation_table = None

    def reread(self):
        self._read_file(self.file)

    @property
    def optional_header_offset(self) -> Offset:
        return self.dos_header.e_lfanew + 4 + sizeof(ImageFileHeader)

    def rewrite_image_nt_headers(self):
        offset = self.dos_header.e_lfanew
        nt_headers_data = bytes(self.nt_headers)[:self.nt_headers_size]
        self.file.seek(offset)
        self.file.write(nt_headers_data)

    def rewrite_data_directory(self):
        data_directory_data = bytes(self.data_directory)[:self.data_directory_size]
        self.file.seek(self.data_directory_offset)
        self.file.write(data_directory_data)

    @property
    def data_directory_offset(self) -> Offset:
        return self.dos_header.e_lfanew + sizeof(self.nt_headers) - sizeof(ImageDataDirectoryArray)

    @property
    def data_directory_size(self) -> int:
        return sizeof(ImageDataDirectory) * self.optional_header.number_of_rva_and_sizes

    @property
    def nt_headers_size(self) -> int:
        # Real size of the optional_header depends on number_of_rva_and_sizes value
        return sizeof(self.nt_headers) - sizeof(ImageDataDirectoryArray) + self.data_directory_size

    @property
    def section_table_offset(self) -> Offset:
        return self.dos_header.e_lfanew + self.nt_headers_size

    @property
    def section_table(self):
        if self._section_table is None:
            n = self.file_header.number_of_sections
            offset = self.section_table_offset
            self._section_table = SectionTable.read(self.file, offset, n)
        return self._section_table

    @property
    def relocation_table(self) -> RelocationTable:
        if self._relocation_table is None:
            rva = self.data_directory.basereloc.virtual_address
            offset = self.section_table.rva_to_offset(rva)
            size = self.data_directory.basereloc.size
            self.file.seek(offset)
            self._relocation_table = RelocationTable.from_file(self.file, size)
        return self._relocation_table

    def add_new_section(self, new_section: Section, data_size: int):
        file = self.file
        sections = self.section_table
        section_alignment = self.optional_header.section_alignment
        file_alignment = self.optional_header.file_alignment
        file_size = align(new_section.pointer_to_raw_data + data_size, file_alignment)
        new_section.size_of_raw_data = file_size - new_section.pointer_to_raw_data

        # Align file size
        file.truncate(file_size)

        # Set the new section virtual size
        new_section.virtual_size = data_size

        # Write the new section info
        write_structure(
            new_section,
            file,
            self.section_table_offset + len(sections) * sizeof(Section)
        )

        # Fix number of sections
        self.file_header.number_of_sections = len(sections) + 1
        # Fix ImageSize field of the PE header
        self.optional_header.size_of_image = align(
            new_section.virtual_address + new_section.virtual_size,
            section_alignment
        )
        self.rewrite_image_nt_headers()

    def info(self):
        entry_point = (self.optional_header.address_of_entry_point
                       + self.optional_header.image_base)
        return (
            f"DOS signature: {self.dos_header.e_magic!r}\n"
            f"e_lfanew: 0x{self.dos_header.e_lfanew:x}\n"
            f"PE signature: {self.nt_headers.signature!r}\n"
            f"Entry point address: 0x{entry_point}\n"
            f"{self.file_header}\n"
            f"{self.optional_header}\n"
            f"{self.data_directory}\n"
            f"{self.section_table}\n"
        )
