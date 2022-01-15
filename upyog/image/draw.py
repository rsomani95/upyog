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


color = lambda r, g, b: f"rgb({r},{g},{b})"


@fastcore.patch
def draw_text(
    self: PIL.Image.Image,
    text: Union[str, List[str]],
    font_size: float = None,
    font_color: Union[tuple, int] = (220, 220, 220),
    font_path: Optional[str] = str(
        Path(__file__).parent.parent.parent / "assets" / "EuroStyleNormal.ttf"
    ),
    location: Literal[
        "bottom",
        "bottom-right",
        "bottom-left",
        "top",
        "top-right",
        "top-left",
    ] = "top",
    font_background: bool = False,
    font_border: bool = True,
    font_size_div_factor: int = 30,
    top_pad_factor: float = 0.001,
):
    """
    Draw `text` on top of `img`. This is done _inplace_

    * text: The text that will be "drawn" on the image. Can be a
              list of strings as well
    * font_size: Explicitly set font-size. Not recommended.
                 See `font_size_div_factor` to scale font size proportionately
    * font_color: An int or tuple of RGB color values
    * font_path: Path to the font file (tested with `.ttf`)
    * location: Where to draw the text? Any combination of
                {bottom,top} + {right,left} where {bottom,top}
                are mandatory
    * font_background: Draw a black rectangle behind the text for clarity.
                       WARNING: This modifies the image size
    * font_size_div_factor: Set font size to img.width/font_size_div_factor
                            Font size is smaller for larger values
    * top_pad_factor: Adjustment for the padding of the text from top. This
                      may need some fiddling depending on the font being used
    """
    img = self

    assert location in [
        "bottom",
        "bottom-right",
        "bottom-left",
        "top",
        "top-right",
        "top-left",
    ]

    if font_size is None:
        font_size = int(img.width / font_size_div_factor)

    if font_path:
        # PIL gives an unintuitive OSError without much useful info
        if not Path(font_path).exists:
            raise FileNotFoundError(f"Couldn't find font file @ {font_path}")
        font = ImageFont.truetype(font_path, size=font_size)

    else:
        font = ImageFont.load_default()
        warnings.warn(
            "Loaded default PIL ImageFont. It's highly recommended you use a custom font as the default font's size cannot be tweaked"
        )

    fcolor = color(*font_color)
    # Check for valid locations

    # Convert text to drawable format
    if isinstance(text, str):
        text = [text]

    if font_background:
        if len(text) > 1:
            warnings.warn(
                f"Drawing a font background with multiple texts will likely result in a misaligned title. Split your code into multiple calls with a dedicated call for the title"
            )
        h = int(font_size * 1.7)
        i = Image.new("RGB", (img.width, h + img.height))

        paste_coords = (0, 0) if "bottom" in location else (0, h)
        i.paste(img, paste_coords)
        img = i

    if "top" in location:
        text = ["\n".join(text)]

    draw = ImageDraw.Draw(img)

    for i, label in enumerate(list(reversed(text))):
        if "bottom" in location or "top" in location:
            w, h = draw.textsize(label, font)

        if "bottom" in location:
            height = img.height - ((i + 1) * font_size * 1.3)

        elif "top" in location:
            height = img.height * font_size * top_pad_factor

        if location == "bottom" or location == "top":
            xy = ((img.width - w) / 2, height)
        elif "-right" in location:
            xy = (((img.width - (w + img.width * 0.01))), height)
        elif "-left" in location:
            xy = (img.width * 0.01, height)
        else:
            y = 1 if i == 0 else i * font_size * 1.5
            xy = (10, y)

        if font_border:
            # thin border
            x, y = xy
            draw.text((x - 1, y), label, font=font, fill="black")
            draw.text((x + 1, y), label, font=font, fill="black")
            draw.text((x, y - 1), label, font=font, fill="black")
            draw.text((x, y + 1), label, font=font, fill="black")

            # thicker border
            draw.text((x - 1, y - 1), label, font=font, fill="black")
            draw.text((x + 1, y - 1), label, font=font, fill="black")
            draw.text((x - 1, y + 1), label, font=font, fill="black")
            draw.text((x + 1, y + 1), label, font=font, fill="black")

        draw.text(xy, text=label, fill=fcolor, font=font)
    return img
