from upyog.imports import *


@fastcore.patch
def __or__(self: Image.Image, other: Image.Image):
    "Horizontally stack two PIL Images"
    assert isinstance(other, Image.Image)
    widths, heights = zip(*(i.size for i in [self, other]))

    new_img = Image.new("RGB", (sum(widths), max(heights)))
    x_offset = 0
    for img in [self, other]:
        new_img.paste(img, (x_offset, 0))
        x_offset += img.size[0]
    return new_img


@fastcore.patch
def __floordiv__(self: Image.Image, other: Image.Image):
    "Vertically stack two PIL Images"
    assert isinstance(other, Image.Image)
    widths, heights = zip(*(i.size for i in [self, other]))

    new_img = Image.new("RGB", (max(widths), sum(heights)))
    y_offset = 0
    for img in [self, other]:
        new_img.paste(img, (0, y_offset))
        y_offset += img.size[1]
    return new_img


def img_join_horizontal(imgs: List[Image.Image]) -> Image.Image:
    return reduce(operator.__or__, imgs)


def img_join_vertical(imgs: List[Image.Image]) -> Image.Image:
    return reduce(operator.__floordiv__, imgs)
