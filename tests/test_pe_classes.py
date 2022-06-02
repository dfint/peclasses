from ctypes import sizeof

from peclasses.pe_classes import (
    ImageDosHeader, ImageFileHeader, DataDirectory, ImageDataDirectory, ImageOptionalHeader, ImageSectionHeader
)


def test_sizes():
    assert sizeof(ImageDosHeader) == 64
    assert sizeof(ImageFileHeader) == 20
    assert sizeof(DataDirectory) == 8
    assert sizeof(ImageDataDirectory) == 8 * 16
    assert sizeof(ImageOptionalHeader) == 224
    assert sizeof(ImageSectionHeader) == 40
