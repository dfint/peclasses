# PECLASSES

[![Tests](https://github.com/dfint/peclasses/actions/workflows/tests.yml/badge.svg)](https://github.com/dfint/peclasses/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/dfint/peclasses/badge.svg?branch=main)](https://coveralls.io/github/dfint/peclasses?branch=main)

This is intended to be a fast, minimalistic, IDE-friendly library for Portable Executable file parsing.

Also it contains `AnnotatedStructure` base class which allows to declare 
[ctypes structures](https://docs.python.org/3/library/ctypes.html#structures-and-unions) in the [dataclass](https://docs.python.org/3/library/dataclasses.html) style, e.g.:

```python
from ctypes import c_int
from peclasses.annotated_structure import AnnotatedStructure


class POINT(AnnotatedStructure):
    x: c_int
    y: c_int
```

instead of:

```python
from ctypes import Structure, c_int


class POINT(Structure):
     _fields_ = [("x", c_int),
                 ("y", c_int)]
```

Derived from the [dfrus](https://github.com/dfint/dfrus) project.

## Features

- As is **peclasses** is IDE-friendly, i.e. an IDE will show you hints about fields of structures;
- it is pythonic, i.e. names of structures and their fields comply to PEP8 rules;
- ease to add new structures.

## Cons

- Comparing to **pefile**, **peclasses** is in the early stages of development and may lack some features;
- pythonic name style may confuse some of the library users;
- it's not tested against a variety of real life species of portable executable, and may not be suitable for eg. malware analysis (at least without some improvements).
