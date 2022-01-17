from .draw import *


def draw_rule_of_thirds(img: Image.Image, thickness=5, opacity=0.4):
    img = img.draw_vertical_bars([1 / 3, 2 / 3], thickness=thickness, opacity=opacity)
    img = img.draw_horizontal_bars([1 / 3, 2 / 3], thickness=thickness, opacity=opacity)
    return img
