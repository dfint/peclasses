from ctypes import c_char, c_ushort, c_uint, c_ubyte, c_ulonglong
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


class ImageDataDirectory(AnnotatedStructure):
    virtual_address: c_uint
    size: c_uint


class ImageDataDirectoryArray(AnnotatedStructure):
    export: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_EXPORT == 0
    import_directory: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_IMPORT == 1
    resource: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_RESOURCE == 2
    exception: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_EXCEPTION == 3
    security: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_SECURITY == 4
    basereloc: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_BASERELOC == 5
    debug: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_DEBUG == 6
    architecture: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_ARCHITECTURE == 7
    globalptr: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_GLOBALPTR == 8
    tls: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_TLS == 9
    load_config: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG == 10
    bound_import: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT == 11
    iat: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_IAT == 12
    delay_import: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT == 13
    com_descriptor: ImageDataDirectory  # IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR == 14
    reserved: ImageDataDirectory


class OptionalHeaderVersionMagic(IntEnum):
    IMAGE_NT_OPTIONAL_HDR32_MAGIC = 0x10b
    IMAGE_NT_OPTIONAL_HDR64_MAGIC = 0x20b
    IMAGE_ROM_OPTIONAL_HDR_MAGIC = 0x107


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
    data_directory: ImageDataDirectoryArray


class ImageNTHeaders(AnnotatedStructure):
    signature: c_char * 4
    file_header: ImageFileHeader
    optional_header: ImageOptionalHeader


class ImageOptionalHeader64(AnnotatedStructure):
    magic: c_ushort
    major_linker_version: c_ubyte
    minor_linker_version: c_ubyte
    size_of_code: c_uint
    size_of_initialized_data: c_uint
    size_of_uninitialized_data: c_uint
    address_of_entry_point: c_uint
    base_of_code: c_uint
    image_base: c_ulonglong
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
    size_of_stack_reserve: c_ulonglong
    size_of_stack_commit: c_ulonglong
    size_of_heap_reserve: c_ulonglong
    size_of_heap_commit: c_ulonglong
    loader_flags: c_uint
    number_of_rva_and_sizes: c_uint
    data_directory: ImageDataDirectoryArray


class ImageNTHeaders64(AnnotatedStructure):
    signature: c_char * 4
    file_header: ImageFileHeader
    optional_header: ImageOptionalHeader64


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
