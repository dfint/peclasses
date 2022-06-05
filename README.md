# PECLASSES

[![Tests](https://github.com/dfint/peclasses/actions/workflows/tests.yml/badge.svg)](https://github.com/dfint/peclasses/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/dfint/peclasses/badge.svg?branch=main)](https://coveralls.io/github/dfint/peclasses?branch=main)

This is intended to be a fast, minimalistic, IDE-friendly library for Portable Executable file parsing.

Also, it contains [`AnnotatedStructure` and `AnnotatedUnion`](https://github.com/dfint/peclasses/blob/main/peclasses/annotated_structure.py) base classes which allow to declare 
[ctypes structures](https://docs.python.org/3/library/ctypes.html#structures-and-unions) in the [dataclass](https://docs.python.org/3/library/dataclasses.html) style.

Derived from the [dfrus](https://github.com/dfint/dfrus) project.

## Features

- As is **peclasses** is IDE-friendly, i.e. an IDE will show you hints about fields of structures;
- it is pythonic, i.e. names of structures and their fields comply to PEP8 rules;
- ease to add new structures.

## Cons

- Comparing to **pefile**, **peclasses** is in the early stages of development and may lack some features;
- pythonic name style may confuse some of the library users;
- it's not tested against a variety of real life species of portable executable, and may not be suitable for eg. malware analysis (at least without some improvements).
