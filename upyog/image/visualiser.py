from upyog.imports import *
from upyog.image.draw import *
from upyog.image.composition import *
from upyog.image.draw import TEXT_POSITIONS, DEFAULT_FONT_PATH


__all__ = ["Visualiser"]


class Visualiser:
    """Wrapper around a PIL Image for drawing annotations with a fluent API.

    Use this class to overlay shapes, bounding boxes, labels, and text on images.
    The internal image is copied on construction and mutated by each draw call.
    Most drawing methods return ``self.img`` (the PIL Image) so you can chain
    calls or pass the result elsewhere; ``draw_rule_of_thirds`` returns ``self``.
    Implements ``_repr_png_`` for direct display in Jupyter notebooks.

    **Conventions**
        * **xyxy** — Bounding box as ``(x1, y1, x2, y2)`` in pixel coordinates
          (top-left and bottom-right). Used by rectangles, ellipses, and text regions.
        * **Colors** — RGB tuples ``(r, g, b)`` with values 0–255, or color names
          (e.g. ``"white"``) where the method accepts a string.
        * **Font** — All text uses the instance ``font_path`` and ``font_size``
          (default 30). The font file must exist on disk.

    Construction
    ------------
    **Direct**
        ``Visualiser(img, font_path=None, font_size=30)`` — ``img`` must be a
        PIL ``Image.Image``. The image is deep-copied. Raises ``TypeError`` if
        not a PIL Image and ``FileNotFoundError`` if ``font_path`` is missing.

    **From numpy**
        * ``fromarray_RGB(img_array, font_path=None, font_size=30)`` — ``img_array``
          shape ``(H, W, 3)``, dtype convertible to uint8. Converts to contiguous
          uint8 and builds a PIL Image.
        * ``fromarray_BGR(img_array, ...)`` — Same as above but flips channels
          so BGR becomes RGB (e.g. for OpenCV arrays).

    **From file**
        ``from_file(filepath, font_path=None, font_size=30)`` — Loads with
        ``Image.open(filepath).convert("RGB")``. ``filepath`` can be any
        path-like object.

    Properties
    ----------
    **size** — ``(width, height)`` of the current image (read-only).

    Shapes (rectangles, ellipses, circles, keypoints)
    -------------------------------------------------
    **draw_rectangle** (xyxy, fill=(255,255,255), opacity=0.25, width=None)
        Draw one rectangle. ``fill`` is RGB; ``width=None`` draws a filled
        rectangle, otherwise an outline of that pixel width.

    **draw_rectangles** (xyxys, fill=..., opacity=0.25, width=None)
        Draw multiple rectangles. ``xyxys`` is a list of ``(x1,y1,x2,y2)`` tuples.

    **draw_rounded_rectangle** (xyxy, radius=10, color="white", opacity=1.0, width=3)
        One rounded-corner rectangle. ``color`` can be name or RGB. Outline only.

    **draw_rounded_rectangles** (xyxys, radius=10, color="white", opacity=1.0)
        Multiple rounded rectangles (same style for all).

    **draw_ellipse** (xyxy, fill=(255,255,255), opacity=0.8)
        Ellipse inscribed in the xyxy box.

    **draw_circle** (xy, radius, fill=(255,255,255), opacity=0.8)
        Circle centered at ``(x, y)`` with given ``radius`` in pixels.

    **draw_keypoints** (xys, fill=(255,255,255), opacity=0.8, radius=None, dynamic_radius=True)
        ``xys`` is a list of ``(x, y)`` pixel coordinates. If ``dynamic_radius=True``,
        radius scales with image size; otherwise use ``radius`` (pixels).

    Bounding boxes with labels
    --------------------------
    **draw_bbox** (xyxy, label=None, label_transform=str.title, label_location="bottom",
    confidence=None, style="rounded", corner_radius=10, box_fill=(255,255,255),
    font_fill=(255,255,255), font_bordered=False, font_background=True,
    font_background_opacity=0.15, font_pad=0.03, border_opacity=1.0, border_width=3)
        Draw a box (rounded or sharp corners) and optionally a label inside.
        * ``label`` — Text shown in the box; transformed by ``label_transform``
          (default: title case).
        * ``confidence`` — Float 0–1; displayed as percentage and appended to
          label if both are given (e.g. ``"Cat: 87.3%"``).
        * ``style`` — ``"rounded"`` (uses ``corner_radius``) or ``"sharp"``.
        * ``label_location`` — ``"top"`` or ``"bottom"`` within the box.
        * ``font_*`` — Label text color, border, background strip, padding.
        Returns ``self.img``.

    Bars and grid
    -------------
    **draw_vertical_bars** (width_percentages, fill=(255,255,255), thickness=5, opacity=0.4)
        Vertical lines at given x-positions. ``width_percentages``: list of floats
        in 0–1 (e.g. ``[0.33, 0.66]``) or tuples for (position, color) per line.

    **draw_horizontal_bars** (height_percentages, fill=..., thickness=5, opacity=0.4)
        Horizontal lines at given y-positions (same percentage convention).

    **draw_rule_of_thirds** (thickness=5, opacity=0.4)
        Draws vertical and horizontal lines at 1/3 and 2/3 of width/height.
        Returns ``self`` (not ``self.img``).

    Text
    ----
    **draw_text_within_xyxy** (xyxy, label, font_pad, font_fill, label_location,
    font_bordered=False, font_bg=True, font_bg_opacity=0.15)
        Renders ``label`` inside the xyxy region. ``font_pad`` is padding as a
        fraction of region size. ``label_location``: ``"top"`` or ``"bottom"``.
        ``font_bg`` adds a semi-transparent strip behind the text.

    **draw_text** (text, position, font_border=False, font_color=(255,255,255),
    font_border_color=(0,0,0), padding=0.03, line_spacing=1.3,
    height_constraints=(0.0,1.0), width_constraints=(0.0,1.0))
        Draw text at a fixed position. ``text``: single string or list of strings
        (multi-line; ``line_spacing`` applies). ``position`` must be one of
        ``TEXT_POSITIONS``: e.g. ``"top_left"``, ``"top_center"``, ``"center"``,
        ``"bottom_right"`` (see ``upyog.image.draw.TEXT_POSITIONS`` for full list).
        ``padding``: fraction of image size or pixel int. Constraints are (min, max)
        fractions for the text box. Returns the modified image (same as ``self.img``).

    **caption** (text, color=(255,255,255))
        Full-image caption at the bottom: large padded text, no background strip,
        bordered. Uses the whole image as the xyxy region.

    **title** (text, color=(255,255,255))
        Same as caption but text at the top of the image.

    Example
    -------
    >>> v = Visualiser.from_file("photo.jpg")
    >>> v.draw_bbox((10, 10, 200, 150), label="dog", confidence=0.92)
    >>> v.caption("A dog in the park")
    >>> v.img.save("out.jpg")
    """

    def __init__(self, img: Image.Image, font_path: Optional[str] = None, font_size=30):
        copy = True
        if not isinstance(img, Image.Image):
            raise TypeError(f"Expected a PIL Image, got {type(img)} instead.")
        self.img = deepcopy(img) if copy else img
        self.font_size = font_size
        self.font_path = font_path or DEFAULT_FONT_PATH

        if not Path(self.font_path).exists():
            raise FileNotFoundError(f"{self.font_path} does not exist.")

    @staticmethod
    def _as_int_array(img_array: np.ndarray):
        assert img_array.ndim == 3
        return np.ascontiguousarray(img_array, np.uint8)

    @classmethod
    def fromarray_RGB(
        cls, img_array: np.ndarray, font_path: Optional[str] = None, font_size=30
    ):
        img_array = cls._as_int_array(img_array)
        return cls(Image.fromarray(img_array), font_path, font_size)

    @classmethod
    def fromarray_BGR(
        cls, img_array: np.ndarray, font_path: Optional[str] = None, font_size=30
    ):
        return cls.fromarray_RGB(img_array[:, :, ::-1], font_path, font_size)

    @classmethod
    def from_file(
        cls, filepath: PathLike, font_path: Optional[str] = None, font_size=30
    ):
        return cls(Image.open(filepath).convert("RGB"), font_path, font_size)

    def _repr_png_(self):
        return self.img._repr_png_()

    def __repr__(self):
        return f"Visualiser(img={self.img}, font_path={self.font_path}"

    @property
    def size(self):
        return self.img.size

    def draw_rectangle(
        self,
        xyxy: tuple,
        fill: Optional[tuple] = (255, 255, 255),
        opacity=0.25,
        width=None,
    ):
        self.img = draw_rectangle(self.img, xyxy, fill, opacity, width)
        return self.img

    def draw_rectangles(
        self,
        xyxys: List[tuple],
        fill: Optional[tuple] = (255, 255, 255),
        opacity=0.25,
        width=None,
    ):
        for xyxy in xyxys:
            self.img = self.draw_rectangle(xyxy, fill, opacity, width)
        return self.img

    def draw_ellipse(self, xyxy, fill=(255, 255, 255), opacity=0.8):
        self.img = draw_ellipse(self.img, xyxy, fill, opacity)
        return self.img

    def draw_circle(self, xy, radius, fill=(255, 255, 255), opacity=0.8):
        self.img = draw_circle(self.img, xy, radius, fill, opacity)
        return self.img

    def draw_keypoints(
        self,
        xys: List[Tuple[int, int]],
        fill=(255, 255, 255),
        opacity=0.8,
        radius=None,
        dynamic_radius=True,
    ):
        self.img = draw_keypoints(self.img, xys, fill, opacity, radius, dynamic_radius)
        return self.img

    def draw_rounded_rectangle(
        self, xyxy: tuple, radius=10, color="white", opacity=1.0, width=3
    ):
        self.img = draw_rounded_rectangle(self.img, xyxy, radius, color, opacity, width)
        return self.img

    def draw_rounded_rectangles(
        self, xyxys: List[tuple], radius=10, color="white", opacity=1.0
    ):
        for xyxy in xyxys:
            self.img = self.draw_rounded_rectangle(xyxy, radius, color, opacity)
        return self.img

    def draw_vertical_bars(
        self,
        width_percentages: List[Union[float, tuple]],
        fill=(255, 255, 255),
        thickness=5,
        opacity=0.4,
    ):
        self.img = draw_vertical_bars(
            self.img, width_percentages, fill, thickness, opacity
        )
        return self.img

    def draw_horizontal_bars(
        self,
        height_percentages: List[Union[float, tuple]],
        fill=(255, 255, 255),
        thickness=5,
        opacity=0.4,
    ):
        self.img = draw_horizontal_bars(
            self.img, height_percentages, fill, thickness, opacity
        )
        return self.img

    def draw_bbox(
        self,
        xyxy,
        label: Optional[str] = None,
        label_transform: Callable = str.title,
        label_location: Literal["top", "bottom"] = "bottom",
        confidence: Optional[float] = None,
        style: Literal["rounded", "sharp"] = "rounded",
        corner_radius=10,  # Only if `style` == "rounded"
        box_fill=(255, 255, 255),
        font_fill=(255, 255, 255),
        font_bordered=False,
        font_background=True,
        font_background_opacity=0.15,
        font_pad=0.03,
        border_opacity=1.0,
        border_width=3,
    ):

        if style == "sharp":
            self.img = self.draw_rectangle(xyxy, box_fill, border_opacity, border_width)
        elif style == "rounded":
            self.img = self.draw_rounded_rectangle(
                xyxy, corner_radius, box_fill, border_opacity, border_width
            )

        # fmt: off
        if label:      label = label_transform(label)
        if confidence: confidence = round(confidence * 100, 1)

        if   label and confidence:     label = f"{label}: {confidence}%"
        elif label and not confidence: label = label
        elif confidence and not label: label = f"{confidence} %"
        # fmt: on

        self.img = self.draw_text_within_xyxy(
            xyxy,
            label,
            font_pad,
            font_fill,
            label_location,
            font_bordered,
            font_background,
            font_background_opacity,
        )

        return self.img

    def draw_text_within_xyxy(
        self,
        xyxy,
        label,
        font_pad,
        font_fill,
        label_location,
        font_bordered=False,
        font_bg=True,
        font_bg_opacity=0.15,
    ):
        self.img = draw_text_within_xyxy(
            img=self.img,
            xyxy=xyxy,
            label=label,
            font_path=self.font_path,
            base_font_size=self.font_size,
            pad_percentage=font_pad,
            text_color=font_fill,
            location=label_location,
            bordered=font_bordered,
            add_background=font_bg,
            background_opacity=font_bg_opacity,
        )
        return self.img

    def draw_text(
        self,
        text: Union[str, List[str]],
        position: TEXT_POSITIONS,
        font_border=False,
        font_color=(255, 255, 255),
        font_border_color=(0, 0, 0),
        padding: Union[int, float] = 0.03,
        line_spacing: float = 1.3,  # Only used if text is List[str]
        height_constraints: Tuple[int, int] = (0.0, 1.0),
        width_constraints: Tuple[int, int] = (0.0, 1.0),
    ):
        return draw_text(
            img=self.img,
            text=text,
            position=position,
            font_path=self.font_path,
            font_size=self.font_size,
            font_border=font_border,
            font_color=font_color,
            font_border_color=font_border_color,
            padding=padding,
            line_spacing=line_spacing,
            height_constraints=height_constraints,
            width_constraints=width_constraints,
        )

    def caption(self, text: str, color=(255, 255, 255)):
        xyxy = (0, 0, self.img.width, self.img.height)
        self.img = self.draw_text_within_xyxy(
            xyxy, text, 0.05, color, "bottom", font_bg=False, font_bordered=True
        )
        return self.img

    def title(self, text: str, color=(255, 255, 255)):
        xyxy = (0, 0, self.img.width, self.img.height)
        self.img = self.draw_text_within_xyxy(
            xyxy, text, 0.05, color, "top", font_bg=False, font_bordered=True
        )
        return self.img

    def draw_rule_of_thirds(self, thickness=5, opacity=0.4):
        self.draw_vertical_bars([1 / 3, 2 / 3], thickness=thickness, opacity=opacity)
        self.draw_horizontal_bars([1 / 3, 2 / 3], thickness=thickness, opacity=opacity)
        return self
