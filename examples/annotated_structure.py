#!/env/bin python3
from ctypes import c_float, c_int

from peclasses.annotated_structure import AnnotatedStructure


# Structures and unions: https://docs.python.org/3/library/ctypes.html#structures-and-unions
class POINT(AnnotatedStructure):
    x: c_int
    y: c_int


point = POINT(10, 20)
print(point.x, point.y)  # 10 20

point = POINT(y=5)
print(point.x, point.y)  # 0 5

# POINT(1, 2, 3)
# TypeError: too many initializers


class RECT(AnnotatedStructure):
    upperleft: POINT
    lowerright: POINT


rc = RECT(point)
print(rc.upperleft.x, rc.upperleft.y)  # 0 5
print(rc.lowerright.x, rc.lowerright.y)  # 0 0


# Arrays: https://docs.python.org/3/library/ctypes.html#arrays
class MyStruct(AnnotatedStructure):
    a: c_int
    b: c_float
    point_array: POINT * 4


print(len(MyStruct().point_array))
