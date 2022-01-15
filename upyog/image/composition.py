from .draw import *


def _draw_rule_of_thirds(img: Image.Image, thickness=5, opacity=0.4):
    # fmt: off
    return (
        img
        .draw_vertical_bars([1/3, 2/3], thickness, opacity)
        .draw_horizontal_bars([1/3, 2/3], thickness, opacity)
    )
    # fmt: on


@fastcore.patch
def draw_rule_of_thirds(img: Image.Image, thickness=5, opacity=0.4):
    return _draw_rule_of_thirds(img, thickness, opacity)
