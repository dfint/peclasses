from ctypes import sizeof
from typing import BinaryIO, Optional, SupportsBytes

from peclasses.pe_classes import (
    ImageDosHeader, ImageNTHeaders, ImageFileHeader, ImageOptionalHeader, ImageDataDirectory
)
from peclasses.relocation_table import RelocationTable
from peclasses.section_table import SectionTable
from peclasses.utilities import read_structure


class PortableExecutable:
    file: BinaryIO
    image_dos_header: ImageDosHeader
    image_nt_headers: ImageNTHeaders
    image_file_header: ImageFileHeader
    image_optional_header: ImageOptionalHeader
    image_data_directory: ImageDataDirectory
    _section_table: Optional[SectionTable]
    _relocation_table: Optional[RelocationTable]

    def read_file(self, file):
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

    def rewrite_image_nt_headers(self):
        offset = self.image_dos_header.e_lfanew.value
        self.file.seek(offset)
        self.image_nt_headers: SupportsBytes
        self.file.write(bytes(self.image_nt_headers))

    def rewrite_data_directory(self):
        offset = self.image_dos_header.e_lfanew.value + sizeof(ImageNTHeaders) - sizeof(ImageDataDirectory)
        self.file.seek(offset)
        self.image_data_directory: SupportsBytes
        self.file.write(bytes(self.image_data_directory))

    def reread(self):
        self.read_file(self.file)

    def __init__(self, file):
        self.read_file(file)

    @property
    def section_table(self):
        if self._section_table is None:
            n = self.image_file_header.number_of_sections
            offset = self.image_dos_header.e_lfanew.value + sizeof(self.image_nt_headers)
            self._section_table = SectionTable.read(self.file, offset, n)
        return self._section_table

    @property
    def relocation_table(self) -> RelocationTable:
        if self._relocation_table is None:
            rva = self.image_data_directory.basereloc.virtual_address.value
            offset = self.section_table.rva_to_offset(rva)
            size = self.image_data_directory.basereloc.size
            self.file.seek(offset)
            self._relocation_table = RelocationTable.from_file(self.file, size)
        return self._relocation_table

    def info(self):
        entry_point = (self.image_optional_header.address_of_entry_point.value
                       + self.image_optional_header.image_base.value)
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
