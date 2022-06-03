import pytest

from peclasses.section_table import SectionTable, Section


@pytest.fixture
def section_table():
    return SectionTable([
        Section(
            b".text",
            flags=0x60000020,
            pointer_to_raw_data=0x400,
            size_of_raw_data=0xAA9800,
            virtual_address=0x1000,
            virtual_size=0xAA977F
        ),
        Section(
            b".rdata",
            flags=0x40000040,
            pointer_to_raw_data=0xAA9C00,
            size_of_raw_data=0x12CA00,
            virtual_address=0xAAB000,
            virtual_size=0x12C802
        ),
        Section(
            b".data",
            flags=0xC0000040,
            pointer_to_raw_data=0xBD6600,
            size_of_raw_data=0x9A00,
            virtual_address=0xBD8000,
            virtual_size=0xDFC4A4
        ),
        Section(
            b".rsrc",
            flags=0x40000040,
            pointer_to_raw_data=0xBE0000,
            size_of_raw_data=0x1800,
            virtual_address=0x19D5000,
            virtual_size=0x1630
        ),
        Section(
            b".reloc",
            flags=0x42000040,
            pointer_to_raw_data=0xBE1800,
            size_of_raw_data=0xBA200,
            virtual_address=0x19D7000,
            virtual_size=0xBA138
        )
    ])


def test_which_section(section_table):
    assert section_table.which_section(offset=section_table[0].pointer_to_raw_data - 1) == -1
    assert section_table.which_section(offset=section_table[0].pointer_to_raw_data) == 0
    assert section_table.which_section(offset=section_table[0].pointer_to_raw_data + 1) == 0


def test_rva_to_offset(section_table):
    assert (section_table.rva_to_offset(section_table[2].virtual_address + 100)
            == section_table[2].pointer_to_raw_data + 100)

    assert (section_table.offset_to_rva(section_table[3].pointer_to_raw_data + 100)
            == section_table[3].virtual_address + 100)