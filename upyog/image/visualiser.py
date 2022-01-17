from .draw import *
from .composition import *


class Visualiser:
    def __init__(self, img: Image.Image, font_path: Optional[str] = None, font_size=30):
        copy = True
        self.img = deepcopy(img) if copy else img
        self.base_font_size = font_size

        if not font_path:
            self.font_path = str(
                Path(__file__).parent.parent.parent / "assets" / "EuroStyleNormal.ttf"
            )

    def _repr_png_(self):
        return self.img._repr_png_()

    def __repr__(self):
        return f"Visualiser(img={self.img}, font_path={self.font_path}"

    @property
    def size(self):
        return self.img.size

    def draw_rectangle(
        self, xyxy: tuple, fill: Optional[tuple] = (255, 255, 255), opacity=0.25
    ):
        self.img = draw_rectangle(self.img, xyxy, fill, opacity)
        return self.img

    def draw_rectangles(
        self, xyxys: List[tuple], fill: Optional[tuple] = (255, 255, 255), opacity=0.25
    ):
        for xyxy in xyxys:
            self.img = self.draw_rectangle(xyxy, fill, opacity)
        return self.img

    def draw_rounded_rectangle(
        self, xyxy: tuple, radius=10, color="white", opacity=1.0
    ):
        self.img = draw_rounded_rectangle(self.img, xyxy, radius, color, opacity)
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
        label: str,
        label_transform: Callable = str.upper,
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
        opacity=1.0,
    ):

        if style == "sharp":
            self.img = self.draw_rectangle(xyxy, box_fill, opacity)
        elif style == "rounded":
            self.img = self.draw_rounded_rectangle(
                xyxy, corner_radius, box_fill, opacity
            )

        label = label_transform(label)
        if confidence:
            label = f"{label}: {confidence*100}%"

        self.img = self.draw_text_within_xyxy(
            xyxy, label, font_pad, font_fill, label_location, font_bordered
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
            base_font_size=self.base_font_size,
            pad_percentage=font_pad,
            text_color=font_fill,
            location=label_location,
            bordered=font_bordered,
            add_background=font_bg,
            background_opacity=font_bg_opacity,
        )
        return self.img

    def caption(self, text: str, color=(255, 255, 255)):
        xyxy = (0, 0, self.img.width, self.img.height)
        self.img = self.draw_text_within_xyxy(
            xyxy, text, 0.05, color, "bottom", font_bg=False, font_bordered=True
        )
        return self.img

    def draw_rule_of_thirds(self, thickness=5, opacity=0.4):
        return draw_rule_of_thirds(self.img, thickness, opacity)
