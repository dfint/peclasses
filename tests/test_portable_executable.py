import os
import tempfile
from pathlib import Path

import pytest

from peclasses.portable_executable import PortableExecutable

code = """
format PE GUI

section '.text' code readable executable
    ret

section '.data' readable writable
    db 0

section '.reloc' data readable discardable fixups
"""


@pytest.fixture
def exe_file():
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        
        asm_file_path = tmpdir / "file.asm"
        exe_file_path = tmpdir / "file.exe"
        
        with open(asm_file_path, "wt") as asm:
            asm.write(code)
        
        os.system(f"fasm {asm_file_path} {exe_file_path}")
        yield exe_file_path


def test_portable_executable_section_table(exe_file):
    with open(exe_file, "rb") as file:
        pe = PortableExecutable(file)
        assert [section.name for section in pe.section_table] == [b'.text', b'.data', b'.reloc']
