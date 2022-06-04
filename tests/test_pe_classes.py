from ctypes import sizeof

from peclasses.pe_classes import (
    ImageDosHeader,
    ImageFileHeader,
    ImageDataDirectory,
    ImageDataDirectoryArray,
    ImageOptionalHeader,
    ImageSectionHeader,
    ImageNTHeaders,
    ImageOptionalHeader64,
    ImageNTHeaders64,
)


def test_sizes():
    assert sizeof(ImageDosHeader) == 64
    assert sizeof(ImageFileHeader) == 20
    assert sizeof(ImageDataDirectory) == 8
    assert sizeof(ImageDataDirectory) == 8
    assert sizeof(ImageDataDirectoryArray) == 8 * 16  # sizeof(ImageDataDirectory) * 16
    assert sizeof(ImageOptionalHeader) == 224
    assert sizeof(ImageOptionalHeader64) == 240
    assert sizeof(ImageSectionHeader) == 40
    assert sizeof(ImageNTHeaders) == 4 + 20 + 224  # 4 + sizeof(ImageFileHeader) + sizeof(ImageOptionalHeader)
    assert sizeof(ImageNTHeaders64) == 4 + 20 + 240  # 4 + sizeof(ImageFileHeader) + sizeof(ImageOptionalHeader64)
