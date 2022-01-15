from upyog.imports import *
from upyog.image.io import *


@fastcore.patch
def __or__(self: Image.Image, other: Image.Image):
    "Horizontally stack two PIL Images"
    assert isinstance(other, Image.Image)
    this_W, this_H = self.size
    that_W, that_H = other.size

    if not this_H == that_H:
        other = other.resize_pad((that_W, this_H))

    widths, heights = zip(*(i.size for i in [self, other]))
    new_img = Image.new("RGB", (sum(widths), max(heights)), 255)

    x_offset = 0
    for img in [self, other]:
        new_img.paste(img, (x_offset, 0))
        x_offset += img.size[0]
    return new_img


@fastcore.patch
def __floordiv__(self: Image.Image, other: Image.Image):
    "Vertically stack two PIL Images"
    assert isinstance(other, Image.Image)
    this_W, this_H = self.size
    that_W, that_H = other.size

    if not this_W == that_W:
        other = other.resize_pad((this_W, that_H))

    widths, heights = zip(*(i.size for i in [self, other]))
    new_img = Image.new("RGB", (max(widths), sum(heights)), 255)

    y_offset = 0
    for img in [self, other]:
        new_img.paste(img, (0, y_offset))
        y_offset += img.size[1]
    return new_img


ImageCollection = Collection[Image.Image]


def img_join_horizontal(imgs: ImageCollection) -> Image.Image:
    return reduce(operator.__or__, imgs)


def img_join_vertical(imgs: ImageCollection) -> Image.Image:
    return reduce(operator.__floordiv__, imgs)


def img_grid(
    imgs: ImageCollection, ncol=3, size_WH: Optional[tuple] = (640, 384), pad=True
):
    start = time.time()

    # fmt: off
    if size_WH:
        if pad: imgs = [img.resize_pad(size_WH) for img in imgs]
        else:   imgs = [img.resize(size_WH) for img in imgs]
    else:
        pass
    # fmt: on

    rows, row = [], []
    for i, img in enumerate(imgs, start=1):
        row += [img]
        if i % ncol == 0:
            rows += [row]
            row = []
    rows += [row]

    # return rows
    print("Creating Grid")
    rows = [img_join_horizontal(row) for row in rows]

    end = time.time()

    return img_join_vertical(rows)


def img_grid(
    imgs: ImageCollection, ncol=3, size_WH: Optional[tuple] = (640, 384), pad=True
):
    from rich.progress import Progress

    with Progress() as prog:
        # fmt: off
        if size_WH:
            if pad: imgs = [img.resize_pad(size_WH) for img in imgs]
            else:   imgs = [img.resize(size_WH) for img in imgs]
        else:
            pass
        # fmt: on

        # Create rows with individual images
        rows, row = [], []
        for i, img in enumerate(imgs, start=1):
            row += [img]
            if i % ncol == 0:
                rows += [row]
                row = []
        rows += [row]

        n_tasks = len(rows) + 1
        task_concat = prog.add_task("Concatenating Rows...", total=n_tasks)
        # print(task_concat.total)
        grid = []

        while not prog.finished:
            for row in rows:
                grid += [img_join_horizontal(row)]
                prog.update(task_concat, advance=1)
                time.sleep(1)

            grid = img_join_vertical(grid)
            prog.update(task_concat, advance=1)

            print(prog)

    return grid
