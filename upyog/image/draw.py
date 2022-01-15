from upyog.imports import *


def _draw_rectangle(
    img: Image.Image, xyxy: tuple, fill: Optional[tuple] = (255, 255, 255), opacity=0.25
):
    new = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(new)
    if fill:
        opacity = int(opacity * 255)
        fill = fill + (opacity,)
    draw.rectangle(xyxy, fill=fill, outline=fill, width=None if fill else 1)

    img = Image.alpha_composite(img.convert("RGBA"), new)
    img = img.convert("RGB")

    return img


def _draw_rectangles(
    img, xyxys: List[tuple], fill: Optional[tuple] = (255, 255, 255), opacity=0.25
):
    for xyxy in xyxys:
        img = _draw_rectangle(img, xyxy, fill, opacity)

    return img


def calc_offset(thickness):
    return int((thickness - 1) / 2)


def _draw_vertical_bars(img, width_percentages, fill, thickness, opacity):
    W, H = img.size
    off = offset = calc_offset(thickness)

    xyxys = []
    for w in width_percentages:
        if isinstance(w, float):
            w = W * w
            xyxys += [(w - off, 0, w + off, H)]
        elif isinstance(w, (tuple, list)):
            assert len(w) == 2
            start, end = w
            xyxys += [(W * start, 0, W * end, H)]

    return _draw_rectangles(img, xyxys, opacity=opacity, fill=fill)


@fastcore.patch
def draw_vertical_bars(
    self: Image.Image,
    width_percentages: List[Union[float, tuple]],
    fill=(255, 255, 255),
    thickness=5,
    opacity=0.4,
):
    return _draw_vertical_bars(self, width_percentages, fill, thickness, opacity)


def _draw_horizontal_bars(img, height_percentages, fill, thickness, opacity):
    W, H = img.size
    off = offset = calc_offset(thickness)

    xyxys = []
    for h in height_percentages:
        if isinstance(h, float):
            h = H * h
            xyxys += [(0, h - off, W, h + off)]
        elif isinstance(h, (tuple, list)):
            assert len(h) == 2
            start, end = h
            xyxys += [(0, H * start, W, H * end)]

    return _draw_rectangles(img, xyxys, opacity=opacity, fill=fill)


@fastcore.patch
def draw_horizontal_bars(
    self: Image.Image,
    height_percentages: List[Union[float, tuple]],
    fill=(255, 255, 255),
    thickness=5,
    opacity=0.4,
):
    return _draw_horizontal_bars(self, height_percentages, fill, thickness, opacity)


@fastcore.patch
def draw_rectangle(self: Image.Image, xyxy: tuple, fill=(255, 255, 255), opacity=0.25):
    "Returns a copy of the image, no modifications are made inplace"
    return _draw_rectangle(self, xyxy, fill, opacity)


@fastcore.patch
def draw_rectangles(
    self: Image.Image, xyxys: List[tuple], fill=(255, 255, 255), opacity=0.25
):
    "Returns a copy of the image, no modifications are made inplace"
    return _draw_rectangles(self, xyxys, fill, opacity)


ImageCollection = Collection[Image.Image]


def img_join_horizontal(imgs: ImageCollection) -> Image.Image:
    return reduce(operator.__or__, imgs)


def img_join_vertical(imgs: ImageCollection) -> Image.Image:
    return reduce(operator.__floordiv__, imgs)


def make_img_grid(
    imgs: ImageCollection, ncol=3, size_WH: Optional[tuple] = (640, 384), pad=True
):
    # fmt: off
    if size_WH:
        if pad: imgs = [img.resize_pad(size_WH) for img in imgs]
        else:   imgs = [img.resize(size_WH) for img in imgs]
    else:
        pass
    # fmt: on

    if ncol == 1:
        return img_join_vertical(imgs)

    from rich.progress import Progress

    with Progress() as prog:
        # Create rows with individual images
        rows, row = [], []
        for i, img in enumerate(imgs, start=1):
            row += [img]
            if i % ncol == 0:
                rows += [row]
                row = []
        if not row == []:
            rows += [row]

        n_tasks = len(rows) + 1
        task_concat = prog.add_task("Concatenating Rows...", total=n_tasks)
        # print(task_concat.total)
        grid = []

        while not prog.finished:
            for row in rows:
                grid += [img_join_horizontal(row)]
                prog.update(task_concat, advance=1)

            grid = img_join_vertical(grid)
            prog.update(task_concat, advance=1)

            print(prog)

    return grid
