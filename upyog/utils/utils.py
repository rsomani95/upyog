from upyog.imports import *
from itertools import islice

__all__ = [
    "flatten", "uniqueify", "get_YYYY_MM_DD", "chunk", "notnone",
    "lmap", "allequal", "zipsafe", "convert_size"
]


def flatten(x: Any) -> List[Any]:
    flattened_list = []
    for item in x:
        if hasattr(item, "__iter__") and not isinstance(item, (str, bytes)):
            [flattened_list.append(i) for i in item]
        else:
            flattened_list.append(item)
    return flattened_list


def uniqueify(x: Collection) -> Collection:
    return sorted(list(set(x)))


def get_YYYY_MM_DD(sep="_") -> str:
    return datetime.now().strftime(f"%Y{sep}%m{sep}%d")


# Borrowed from https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunk(items: Collection[Any], size: int, strict=True) -> list:
    if strict:
        assert len(items) % size == 0

    items = iter(items)
    return list(iter(lambda: tuple(islice(items, size)), ()))


# Borrowed from icevision.utils
def notnone(x):
    return x is not None


def lmap(f, xs):
    return list(map(f, xs)) if notnone(xs) else None


def allequal(l):
    return l.count(l[0]) == len(l) if l else True


def zipsafe(*its):
    if not allequal(lmap(len, its)):
        raise ValueError("The elements have different leghts")
    return zip(*its)


# https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
def convert_size(size_bytes: int) -> str:
    "Convert bytes into appropriate unit and return a human readable string for file size"
    if size_bytes == 0:
       return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
