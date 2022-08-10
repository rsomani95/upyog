from upyog.imports import *
from itertools import islice

__all__ = [
    "flatten", "uniqueify", "get_YYYY_MM_DD", "chunk", "notnone",
    "lmap", "allequal", "zipsafe"
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
