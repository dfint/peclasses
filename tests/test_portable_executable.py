import os
import tempfile
from pathlib import Path

import pytest

from peclasses.pe_classes import ImageSectionHeader
from peclasses.portable_executable import PortableExecutable


@pytest.fixture
def exe_file():
    asm_code = """
        format PE GUI
    
        section '.text' code readable executable
            ret
    
        section '.data' data readable writable
            db 0
    
        section '.reloc' data readable discardable fixups
        """

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        
        asm_file_path = tmpdir / "file.asm"
        exe_file_path = tmpdir / "file.exe"
        
        with open(asm_file_path, "wt") as asm_file:
            asm_file.write(asm_code)
        
        os.system(f"fasm {asm_file_path} {exe_file_path}")
        yield exe_file_path


def test_portable_executable_section_table(exe_file):
    chars = ImageSectionHeader.Characteristics
    with open(exe_file, "rb") as file:
        pe = PortableExecutable(file)
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
