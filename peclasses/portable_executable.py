from ctypes import sizeof
from typing import BinaryIO, Optional

from peclasses.pe_classes import (
    ImageDosHeader, ImageNTHeaders, ImageFileHeader, ImageOptionalHeader, ImageDataDirectory
)
from peclasses.relocation_table import RelocationTable
from peclasses.section_table import SectionTable, Section
from peclasses.utilities import read_structure, write_structure, align


class PortableExecutable:
    file: BinaryIO
    image_dos_header: ImageDosHeader
    image_nt_headers: ImageNTHeaders
    image_file_header: ImageFileHeader
    image_optional_header: ImageOptionalHeader
    image_data_directory: ImageDataDirectory
    _section_table: Optional[SectionTable]
    _relocation_table: Optional[RelocationTable]

    def __init__(self, file):
        self._read_file(file)

    def _read_file(self, file):
        self.file = file
        self.file.seek(0)
        self.image_dos_header = read_structure(ImageDosHeader, file)
        assert self.image_dos_header.e_magic == b"MZ"
        self.image_nt_headers = read_structure(ImageNTHeaders, file, self.image_dos_header.e_lfanew)
        assert self.image_nt_headers.signature == b"PE"
        self.image_file_header = self.image_nt_headers.image_file_header
        self.image_optional_header = self.image_nt_headers.image_optional_header
        self.image_data_directory = self.image_optional_header.image_data_directory
        self._section_table = None
        self._relocation_table = None

    def reread(self):
        self._read_file(self.file)

    def rewrite_image_nt_headers(self):
        offset = self.image_dos_header.e_lfanew
        write_structure(self.image_nt_headers, self.file, offset)

    def rewrite_data_directory(self):
        offset = self.image_dos_header.e_lfanew + sizeof(ImageNTHeaders) - sizeof(ImageDataDirectory)
        write_structure(self.image_data_directory, self.file, offset)

    @property
    def section_table(self):
        if self._section_table is None:
            n = self.image_file_header.number_of_sections
            offset = self.image_dos_header.e_lfanew + sizeof(self.image_nt_headers)
            self._section_table = SectionTable.read(self.file, offset, n)
        return self._section_table

    @property
    def relocation_table(self) -> RelocationTable:
        if self._relocation_table is None:
            rva = self.image_data_directory.basereloc.virtual_address
            offset = self.section_table.rva_to_offset(rva)
            size = self.image_data_directory.basereloc.size
            self.file.seek(offset)
            self._relocation_table = RelocationTable.from_file(self.file, size)
        return self._relocation_table

    def add_new_section(self, new_section: Section, data_size: int):
        file = self.file
        sections = self.section_table
        section_alignment = self.image_optional_header.section_alignment
        file_alignment = self.image_optional_header.file_alignment
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
            self.image_dos_header.e_lfanew + sizeof(self.image_nt_headers) + len(sections) * sizeof(Section)
        )

        # Fix number of sections
        self.image_file_header.number_of_sections = len(sections) + 1
        # Fix ImageSize field of the PE header
        self.image_optional_header.size_of_image = align(
            new_section.virtual_address + new_section.virtual_size,
            section_alignment
        )
        self.rewrite_image_nt_headers()

    def info(self):
        entry_point = (self.image_optional_header.address_of_entry_point
                       + self.image_optional_header.image_base)
        return (
            f"DOS signature: {self.image_dos_header.e_magic!r}\n"
            f"e_lfanew: 0x{self.image_dos_header.e_lfanew:x}\n"
            f"PE signature: {self.image_nt_headers.signature!r}\n"
            f"Entry point address: 0x{entry_point}\n"
            f"{self.image_file_header}\n"
            f"{self.image_optional_header}\n"
            f"{self.image_data_directory}\n"
            f"{self.section_table}\n"
        )
