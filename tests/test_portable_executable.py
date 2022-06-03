import os
import tempfile
from io import BytesIO
from pathlib import Path

import pytest

from peclasses.pe_classes import ImageSectionHeader
from peclasses.portable_executable import PortableExecutable
from peclasses.section_table import Section
from peclasses.utilities import align

chars = ImageSectionHeader.Characteristics


def compile_asm(asm_code: str):
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)

        asm_file_path = tmpdir / "file.asm"
        exe_file_path = tmpdir / "file.exe"

        with open(asm_file_path, "wt") as asm_file:
            asm_file.write(asm_code)

        os.system(f"fasm {asm_file_path} {exe_file_path}")
        with open(exe_file_path, "rb") as exe_file:
            exe_file_data = exe_file.read()

        return exe_file_data


@pytest.fixture
def exe_file():
    asm_code = """
        format PE GUI
    
        section '.text' code readable executable
            mov eax, some_string
            ret
    
        section '.data' data readable writable
            some_string db 'some string', 0
    
        section '.reloc' data readable discardable fixups
        """

    return BytesIO(compile_asm(asm_code))


@pytest.fixture
def exe64_file():
    asm_code = """
        format PE64 GUI

        section '.text' code readable executable
            mov rax, some_string
            ret

        section '.data' data readable writable
            some_string db 'some string', 0

        section '.reloc' data readable discardable fixups
        """

    return BytesIO(compile_asm(asm_code))


def test_portable_executable_section_table(exe_file):
    pe = PortableExecutable(exe_file)
    assert [(section.name, section.characteristics) for section in pe.section_table] == [
        (
            b'.text',
            chars.IMAGE_SCN_CNT_CODE | chars.IMAGE_SCN_MEM_READ | chars.IMAGE_SCN_MEM_EXECUTE
        ),
        (
            b'.data',
            chars.IMAGE_SCN_CNT_INITIALIZED_DATA | chars.IMAGE_SCN_MEM_READ | chars.IMAGE_SCN_MEM_WRITE
        ),
        (
            b'.reloc',
            chars.IMAGE_SCN_CNT_INITIALIZED_DATA | chars.IMAGE_SCN_MEM_READ | chars.IMAGE_SCN_MEM_DISCARDABLE
        ),
    ]


def test_portable_executable_x64_section_table(exe64_file):
    pe = PortableExecutable(exe64_file)
    assert [(section.name, section.characteristics) for section in pe.section_table] == [
        (
            b'.text',
            chars.IMAGE_SCN_CNT_CODE | chars.IMAGE_SCN_MEM_READ | chars.IMAGE_SCN_MEM_EXECUTE
        ),
        (
            b'.data',
            chars.IMAGE_SCN_CNT_INITIALIZED_DATA | chars.IMAGE_SCN_MEM_READ | chars.IMAGE_SCN_MEM_WRITE
        ),
        (
            b'.reloc',
            chars.IMAGE_SCN_CNT_INITIALIZED_DATA | chars.IMAGE_SCN_MEM_READ | chars.IMAGE_SCN_MEM_DISCARDABLE
        ),
    ]


def test_portable_executable_relocation_table(exe_file):
    pe = PortableExecutable(exe_file)
    relocation_table = pe.relocation_table
    assert len(list(relocation_table)) == 1


def test_add_new_section(exe_file):
    pe = PortableExecutable(exe_file)

    old_section_count = len(pe.section_table)
    new_section_name = b'.new'
    last_section = pe.section_table[-1]
    virtual_address = align(
        last_section.virtual_address + last_section.virtual_size,
        pe.optional_header.section_alignment
    )
    physical_address = align(
        last_section.pointer_to_raw_data + last_section.size_of_raw_data,
        pe.optional_header.file_alignment
    )

    new_section = Section(
        name=new_section_name,
        virtual_address=virtual_address,
        virtual_size=0,  # Will be calculated by add_new_section
        pointer_to_raw_data=physical_address,
        size_of_raw_data=0,  # Will be calculated by add_new_section
        characteristics=0xDEADBEEF
    )

    data_size = 1024  # 1 KiB

    pe.add_new_section(new_section, data_size)
    pe.reread()

    assert len(pe.section_table) == old_section_count + 1
    last_section = pe.section_table[-1]
    assert last_section.name == new_section_name and last_section.characteristics == 0xDEADBEEF
