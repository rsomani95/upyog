from upyog.imports import *

__all__ = ["load_image", "resize_with_padding", "pil_image_to_base64"]


def load_image(fn, mode: Optional[str] = "RGB") -> Image.Image:
    img = Image.open(fn)
    img.load()
    img = img._new(img.im)
    return img.convert(mode) if mode else img


@fastcore.patch
def resize_pad(
    self: Image.Image,
    size_WH: tuple,
    pad_location: Literal["center", "top"] = "center",
    fill: int = 0,
):
    return resize_with_padding(self, size_WH, fill, pad_location)


@fastcore.patch
def to_base64(self: Image.Image):
    return pil_image_to_base64(self)


def get_ratio(from_WH, to_WH) -> np.ndarray:
    W, H = from_WH
    to_W, to_H = to_WH

    return min([to_H / H, to_W / W])


def resize_with_padding(
    img: Image.Image,
    target_WH,
    pad_fill: Union[int, Tuple[int, int, int]] = 0,
    pad_location: Literal["center", "top"] = "center",
    # mode: str = "RGB",
):
    to_W, to_H = target_WH
    W, H = img.size
    orig_mode = img.mode

    ratio = get_ratio(img.size, target_WH)
    W, H = int(ratio * W), int(ratio * H)

    if pad_location == "top":
        box = (0, 0)
    else:
        box = ((to_W - W) // 2, (to_H - H) // 2)

    # Create a new image and paste the resized on it
    if pad_fill:
        if   isinstance(pad_fill, int):          color = (pad_fill, pad_fill, pad_fill)
        elif isinstance(pad_fill, (list,tuple)): color = tuple(pad_fill)
        assert isinstance(color, tuple)
    else:
        color = None

    padded_img = Image.new(orig_mode, (to_W, to_H), color=color)
    try:
        padded_img.paste(img.resize((W, H), Image.Resampling.LANCZOS), box)
    except:
        padded_img.paste(img.resize((W, H), Image.LANCZOS), box)

    return padded_img


def pil_image_to_base64(img: Image.Image) -> str:
    "Convert a PIL image to a base64 encoded string"
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_base64}"
