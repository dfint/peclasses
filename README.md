# PECLASSES

[![Tests](https://github.com/dfint/peclasses/actions/workflows/tests.yml/badge.svg)](https://github.com/dfint/peclasses/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/dfint/peclasses/badge.svg?branch=main)](https://coveralls.io/github/dfint/peclasses?branch=main)

This is intended to be a fast minimalistic library for Portable Executable file parsing.

Also it contains `AnnotatedStructure` base class which allows to declare 
[ctypes structures](https://docs.python.org/3/library/ctypes.html#structures-and-unions) in the [dataclass](https://docs.python.org/3/library/dataclasses.html) style, e.g.:

```python
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
```

instead of:

```python
class ImageDosHeader(Structure):
    _fields_ = [
        ("e_magic", c_char * 2),
        ("e_cblp", c_ushort),
        ("e_cp", c_ushort),
        ("e_crlc", c_ushort),
        ("e_cparhdr", c_ushort),
        ("e_minalloc", c_ushort),
        ...
    ]
```

Derived from the [dfrus](https://github.com/dfint/dfrus) project.
