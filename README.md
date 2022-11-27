# PECLASSES

[![Tests](https://github.com/dfint/peclasses/actions/workflows/tests.yml/badge.svg)](https://github.com/dfint/peclasses/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/dfint/peclasses/badge.svg?branch=main)](https://coveralls.io/github/dfint/peclasses?branch=main)
[![Maintainability](https://api.codeclimate.com/v1/badges/00cfad0a1f5be602411c/maintainability)](https://codeclimate.com/github/dfint/peclasses/maintainability)

This is intended to be a fast, minimalistic, IDE-friendly library for Portable Executable file parsing.

Also, it contains [`AnnotatedStructure` and `AnnotatedUnion`](https://github.com/dfint/peclasses/blob/main/peclasses/annotated_structure.py) base classes which allow to declare 
[ctypes structures](https://docs.python.org/3/library/ctypes.html#structures-and-unions) in the [dataclass](https://docs.python.org/3/library/dataclasses.html) style.

See examples of `AnnotatedStructure` usage here: [examples/annotated_structure.py](https://github.com/dfint/peclasses/examples/annotated_structure.py)

Derived from the [dfrus](https://github.com/dfint/dfrus) project.

## Features

- As is **peclasses** is IDE-friendly, i.e. an IDE will show you hints about fields of structures;
- it is pythonic, i.e. names of structures and their fields comply to PEP8 rules;
- ease to add new structures.

## Cons

- Comparing to [**pefile**](https://github.com/erocarrera/pefile), **peclasses** is in the early stages of development and may lack some features;
- pythonic name style may confuse some library users;
- it's not tested against a variety of real life species of portable executable, and may not be suitable for e.g. malware analysis (at least without some improvements);
- type annotations with types from ctypes can be somewhat misleading: e.g. a structure field can be annotated as `c_uint`,
  ctypes will return its value as plain `int`, but typing tools (such as mypy) will complain that you cannot treat this
  value as `int` (because it's annotated as `c_uint`), so you may need to use [`cast` function from `typing`](https://docs.python.org/3/library/typing.html#typing.cast).
