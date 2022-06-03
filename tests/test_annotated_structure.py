import io
from ctypes import c_int, c_byte, sizeof
from typing import SupportsBytes, cast

from peclasses.annotated_structure import AnnotatedStructure
from peclasses.utilities import write_structure


def test_annotated_structure():
    class Test(AnnotatedStructure):
        field: c_int
        bytes_field: c_byte * 4

    assert sizeof(Test) == 8

    test = Test()

    integer_value = 10
    bytes_value = b"1234"

    test.field = integer_value
    test.bytes_field = type(test.bytes_field)(*bytes_value)
    assert test.field == integer_value
    assert bytes(test.bytes_field) == bytes_value
    assert bytes(cast(SupportsBytes, test)) == integer_value.to_bytes(4, "little") + bytes_value


def test_write_structure():
    class Test(AnnotatedStructure):
        field: c_int
        bytes_field: c_byte * 4

    test = Test()

    integer_value = 10
    bytes_value = b"1234"

    test.field = integer_value
    test.bytes_field = type(test.bytes_field)(*bytes_value)

    file = io.BytesIO()
    write_structure(test, file, 0)
    assert bytes(cast(SupportsBytes, test)) == file.getvalue()
