from upyog.imports import *


def get_fill(fill: Tuple[int, int, int], opacity: float):
    if fill:
        opacity = int(opacity * 255)
        return fill + (opacity,)


def draw_rectangle(
    img: Image.Image,
    xyxy: tuple,
    fill: Optional[tuple] = (255, 255, 255),
    opacity=0.25,
    width=None,
):
    # NOTE: This draws a _filled_ rectangle
    new = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(new)
    fill = get_fill(fill, opacity)
    draw.rectangle(xyxy, fill=fill, outline=fill, width=width)

    img = Image.alpha_composite(img.convert("RGBA"), new)
    img = img.convert("RGB")

    return img


def draw_rectangles(
    img, xyxys: List[tuple], fill: Optional[tuple] = (255, 255, 255), opacity=0.25
):
    for xyxy in xyxys:
        img = draw_rectangle(img, xyxy, fill, opacity)

    return img


# TODO: Use ImageDraw.Draw
def draw_rounded_rectangle(
    img: Image.Image, xyxy: tuple, radius=10, color="white", opacity=1.0, width=3
):
    """Draw a rounded rectangle"""
    from aggdraw import Pen, Draw

    xl, yu, xr, yl = xyxy
    draw = Draw(img)
    pen = Pen(color, opacity=int(opacity * 255), width=width)
    r = radius

    # fmt: off
    draw.line((xl+r/2, yu, xr-r/2, yu), pen)      # Top Horizontal
    draw.arc((xr-r, yu, xr, yu+r), 0, 90, pen)    # Upper right

    draw.line((xr, yu+r/2, xr, yl-r/2), pen)      # Right Vertical
    draw.arc((xr-r, yl-r, xr, yl), 270, 360, pen) # Lower right

    draw.line((xr-r/2, yl, xl+r/2, yl), pen)      # Bottom Horizontal
    draw.arc((xl+r, yl, xl, yl-r), 0, 90, pen)    # Lower left

    draw.line((xl, yl-r/2, xl, yu+r/2), pen)      # Left Vertical
    draw.arc((xl, yu, xl+r, yu+r), 90, 180, pen)  # Upper left
    # fmt: on

    return draw.flush()


def draw_ellipse(img, xyxy, fill=(255, 255, 255), opacity=0.8):
    new = Image.new("RGBA", img.size)
    draw = ImageDraw.Draw(new)
    fill = get_fill(fill, opacity)

    draw.ellipse(xyxy, fill=fill, width=0, outline=None)
    img = Image.alpha_composite(img.convert("RGBA"), new)
    img = img.convert("RGB")

    return img


def draw_circle(img, xy, radius, fill=(255, 255, 255), opacity=0.8):
    x, y, r = *xy, radius
    xyxy = x - r, y - r, x + r, y + r
    return draw_ellipse(img, xyxy, fill, opacity)


def draw_keypoint(
    img, xy, fill=(255, 255, 255), opacity=0.8, radius=None, dynamic_radius=True
):
    radius = radius or get_dynamic_radius(img)
    return draw_circle(img, xy, radius, fill, opacity)


def draw_keypoints(
    img, xys, fill=(255, 255, 255), opacity=0.8, radius=None, dynamic_radius=True
):
    fills = None
    if fill:
        if not isinstance(fill[0], (list, tuple)):
            fills = [fill] * len(xys)
        else:
            fills = fill

    for xy, fill in zip(xys, fills):
        img = draw_keypoint(img, xy, fill, opacity, radius, dynamic_radius)
    return img


def get_dynamic_radius(img):
    # Borrowed from `icevision.draw_keypoints`
    w, h = img.size
    area = h * w
    r = int(0.01867599 * (area ** 0.4422045))
    return max(r, 1)


def calc_offset(thickness):
    return int((thickness - 1) / 2)


def draw_vertical_bars(img, width_percentages, fill, thickness, opacity):
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

    return draw_rectangles(img, xyxys, opacity=opacity, fill=fill)


def draw_horizontal_bars(img, height_percentages, fill, thickness, opacity):
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

    return draw_rectangles(img, xyxys, opacity=opacity, fill=fill)


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
    self: Image.Image,
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

        draw, _ = _write_text(
            label, xy, draw, font, bordered=font_border, border_color="black"
        )
    return img


def _write_text(
    text,
    xy,
    draw: ImageDraw.Draw,
    font: ImageFont.ImageFont,
    bordered=True,
    border_color="black",
    font_color="white",
    anchor=None,
):
    label = text
    x, y = xy
    if bordered:
        draw.text((x - 1, y), label, border_color, font, anchor)
        draw.text((x + 1, y), label, border_color, font, anchor)
        draw.text((x, y - 1), label, border_color, font, anchor)
        draw.text((x, y + 1), label, border_color, font, anchor)

        # thicker border
        draw.text((x - 1, y - 1), label, border_color, font, anchor)
        draw.text((x + 1, y - 1), label, border_color, font, anchor)
        draw.text((x - 1, y + 1), label, border_color, font, anchor)
        draw.text((x + 1, y + 1), label, border_color, font, anchor)

    try:
        draw.text(xy, text, font_color, font, anchor)
    except OSError as e:
        msg = f"Failed to write text {text} due to error: {e}"
        warnings.warn(msg)

    text_xyxy = draw.textbbox(xy, text, font, anchor)

    return draw, text_xyxy


def draw_text_within_xyxy(
    img: Image.Image,
    xyxy: tuple,
    label: str,
    font_path: str,
    base_font_size=20,
    pad_percentage: float = 0.03,
    text_color=(255, 255, 255),
    bordered: bool = False,
    add_background: bool = True,
    background_fill=(0, 0, 0),
    background_opacity=0.15,
    location: Literal["bottom", "top"] = "bottom",
):
    box = Box(xyxy)
    draw = ImageDraw.Draw(img)
    font = ImageFont.FreeTypeFont(font_path, size=base_font_size)
    _font = font
    pad = box.height * pad_percentage

    # Dynamically adjust font size to fit the bounding box
    text_box = draw.textbbox(box.bottom_center, label, font, anchor="mt")
    text_box = Box(text_box)
    if location == "bottom":
        text_box.adjust("y2", -pad)
    else:
        text_box.adjust("y1", pad)

    try:
        while not (text_box.height > box.height) and (text_box.width > box.width):
            font = ImageFont.FreeTypeFont(font_path, size=base_font_size)
            text_box = Box(draw.textbbox(box.bottom_center, label, font, anchor="mt"))
            text_box.adjust("x1", -pad)
            text_box.adjust("x2", pad)
            base_font_size -= 1

        _box = deepcopy(box)
        if location == "bottom":
            _box.adjust("y2", -pad)
        else:
            _box.adjust("y1", pad)

        text_xyxy = _box.bottom_center if location == "bottom" else _box.top_center
        anchor = "ms" if location == "bottom" else "mt"
        draw, text_xyxy = _write_text(
            label,
            text_xyxy,
            draw,
            font,
            bordered=bordered,
            border_color="black",
            font_color=text_color,
            anchor=anchor,
        )

        if add_background:
            # print(f"Before: {text_xyxy}")
            _xyxy = Box(text_xyxy)
            pad_x = _xyxy.height * 0.025
            pad_y = _xyxy.height * 0.03
            print(pad)
            _xyxy.adjust("y1", -pad_y)
            _xyxy.adjust("x1", -pad_x)
            _xyxy.adjust("x2", pad_x)
            _x1, _y1, _x2, _y2 = _xyxy.xyxy

            # fmt: off
            # FIXME: yuck...
            x1,y1,x2,y2 = xyxy
            if _x1 < x1: _x1 = x1
            if _x2 > x2: _x2 = x2
            if _y2 > y2: _y2 = y2
            # if _y1 < y1: _y1 = xyxy[1]
            # fmt: on

            img = draw_rectangle(
                img, (_x1, _y1, _x2, _y2), background_fill, background_opacity
            )
    except Exception as e:
        larger_factor = text_box.area / box.area
        msg = f"Failed to resize text. Estimated font size is {larger_factor}x larger than bbox area. Exception={e}"
        warnings.warn(msg)

    return img


class Box:
    def __init__(self, xyxy):
        self._xyxy = xyxy
        self.x1, self.y1, self.x2, self.y2 = xyxy
        self.setup()

    def pad(self, amt):
        self.adjust("y1", -amt)
        self.adjust("x1", -amt)
        self.adjust("x2", amt)
        self.adjust("y2", amt)

    def adjust(self, dim: str, amt):
        assert dim in ["x1", "x2", "y1", "y2"]
        setattr(self, dim, getattr(self, dim) + amt)
        self.setup()

    def setup(self):
        self._dimensions()
        self._centers()
        self._corners()
        self._points()

    def _dimensions(self):
        self.height = self.y2 - self.y1
        self.width = self.x2 - self.x1
        self.area = self.height * self.width

    def _centers(self):
        self.center_horz = self.x1 + self.width / 2
        self.center_vert = self.y1 + self.height / 2
        self.center = (self.center_horz, self.center_vert)

    def _corners(self):
        self.top_left = (self.x1, self.y1)
        self.bottom_right = (self.x2, self.y2)
        self.top_right = (self.x2, self.y1)
        self.bottom_left = (self.x1, self.y1)

    def _points(self):
        self.top_center = (self.center_horz, self.y1)
        self.bottom_center = (self.center_horz, self.y2)
        self.right_center = (self.x2, self.center_vert)
        self.left_center = (self.x1, self.center_vert)

    @property
    def cxcywh(self):
        return (self.center_horz, self.center_vert, self.width, self.height)

    @property
    def xyxy(self):
        return (self.x1, self.y1, self.x2, self.y2)

    def __repr__(self):
        return f"Box({self.x1}, {self.y1}, {self.x2}, {self.y2})"
