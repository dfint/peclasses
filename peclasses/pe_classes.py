from ctypes import c_char, c_ushort, c_uint, c_ubyte
from enum import IntEnum

from peclasses.annotated_structure import AnnotatedStructure, AnnotatedUnion


class ImageDosHeader(AnnotatedStructure):
    e_magic: c_char * 2
    e_cblp: c_ushort
    e_cp: c_ushort
    e_crlc: c_ushort
    e_cparhdr: c_ushort
    e_minalloc: c_ushort
    e_maxalloc: c_ushort
    e_ss: c_ushort
    e_sp: c_ushort
    e_csum: c_ushort
    e_ip: c_ushort
    e_cs: c_ushort
    e_lfarlc: c_ushort
    e_ovno: c_ushort
    e_res: c_ushort * 4
    e_oemid: c_ushort
    e_oeminfo: c_ushort
    e_res2: c_ushort * 10
    e_lfanew: c_uint


class ImageFileHeader(AnnotatedStructure):
    machine: c_ushort
    number_of_sections: c_ushort
    timedate_stamp: c_uint
    pointer_to_symbol_table: c_uint
    number_of_symbols: c_uint
    size_of_optional_header: c_ushort
    characteristics: c_ushort


class DataDirectory(AnnotatedStructure):
    virtual_address: c_uint
    size: c_uint


class ImageDataDirectory(AnnotatedStructure):
    export: DataDirectory
    import_directory: DataDirectory
    resource: DataDirectory
    exception: DataDirectory
    security: DataDirectory
    basereloc: DataDirectory
    debug: DataDirectory
    copyright: DataDirectory
    globalptr: DataDirectory
    tls: DataDirectory
    load_config: DataDirectory
    bound_import: DataDirectory
    iat: DataDirectory
    delay_import: DataDirectory
    com_descriptor: DataDirectory
    reserved: DataDirectory


class ImageOptionalHeader(AnnotatedStructure):
    magic: c_ushort
    major_linker_version: c_ubyte
    minor_linker_version: c_ubyte
    size_of_code: c_uint
    size_of_initialized_data: c_uint
    size_of_uninitialized_data: c_uint
    address_of_entry_point: c_uint
    base_of_code: c_uint
    base_of_data: c_uint
    image_base: c_uint
    section_alignment: c_uint
    file_alignment: c_uint
    major_operating_system_version: c_ushort
    minor_operating_system_version: c_ushort
    major_image_version: c_ushort
    minor_image_version: c_ushort
    major_subsystem_version: c_ushort
    minor_subsystem_version: c_ushort
    win32_version_value: c_uint
    size_of_image: c_uint
    size_of_headers: c_uint
    check_sum: c_uint
    subsystem: c_ushort
    dll_characteristics: c_ushort
    size_of_stack_reserve: c_uint
    size_of_stack_commit: c_uint
    size_of_heap_reserve: c_uint
    size_of_heap_commit: c_uint
    loader_flags: c_uint
    number_of_rva_and_sizes: c_uint
    image_data_directory: ImageDataDirectory


class ImageNTHeaders(AnnotatedStructure):
    signature: c_char * 4
    image_file_header: ImageFileHeader
    image_optional_header: ImageOptionalHeader


class ImageSectionHeader(AnnotatedStructure):
    class Characteristics(IntEnum):
        IMAGE_SCN_CNT_CODE = 0x00000020
        IMAGE_SCN_CNT_INITIALIZED_DATA = 0x00000040
        IMAGE_SCN_CNT_UNINITIALIZED_DATA = 0x00000080
        IMAGE_SCN_MEM_DISCARDABLE = 0x02000000
        IMAGE_SCN_MEM_SHARED = 0x10000000
        IMAGE_SCN_MEM_EXECUTE = 0x20000000
        IMAGE_SCN_MEM_READ = 0x40000000
        IMAGE_SCN_MEM_WRITE = 0x80000000

    class _Misc(AnnotatedUnion):
        physical_address: c_uint
        virtual_size: c_uint

    name: c_char * 8
    misc: _Misc
    virtual_address: c_uint
    size_of_raw_data: c_uint
    pointer_to_raw_data: c_uint
    pointer_to_relocations: c_uint
    pointer_to_linenumbers: c_uint
    number_of_relocations: c_ushort
    number_of_linenumbers: c_ushort
    characteristics: c_uint

    @property
    def virtual_size(self):
        return self.misc.virtual_size

    @virtual_size.setter
    def virtual_size(self, value):
        self.misc.virtual_size = value
