"""
Base classes which allow to declare ctypes structures in the dataclass style, e.g.:

```
from ctypes import c_int
from peclasses.annotated_structure import AnnotatedStructure


class POINT(AnnotatedStructure):
    x: c_int
    y: c_int
```

instead of:

```
from ctypes import Structure, c_int


class POINT(Structure):
     _fields_ = [("x", c_int),
                 ("y", c_int)]
```

For real-life examples see pe_classes.py module.
"""

from ctypes import Structure, Union


class AnnotatedStructureMetaclass(type(Structure)):
    def __new__(mcs, name, bases, namespace, **kwargs):
        annotations = namespace.get("__annotations__")
        if annotations:
            namespace["_fields_"] = [(name, declared_type) for name, declared_type in annotations.items()]
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class AnnotatedStructure(Structure, metaclass=AnnotatedStructureMetaclass):
    """
    A wrapper for Structure from ctypes which automatically adds _fields_
    and fills it according to type annotations from the class
    """


class AnnotatedUnionMetaclass(type(Union)):
    def __new__(mcs, name, bases, namespace, **kwargs):
        annotations = namespace.get("__annotations__")
        if annotations:
            namespace["_fields_"] = [(name, declared_type) for name, declared_type in annotations.items()]
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class AnnotatedUnion(Union, metaclass=AnnotatedUnionMetaclass):
    ...
