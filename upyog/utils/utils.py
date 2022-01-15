from upyog.imports import *


def flatten(x: Any) -> List[Any]:
    flattened_list = []
    for item in x:
        if isinstance(item, (tuple, list)):
            [flattened_list.append(i) for i in item]
        else:
            flattened_list.append(item)
    return flattened_list


def uniqueify(x: Collection) -> Collection:
    return sorted(list(set(x)))
