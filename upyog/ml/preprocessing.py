from upyog.ml.imports import *


__all__ = ["IMAGENET_MEAN", "IMAGENET_STDEV", "PreprocessingParams"]


IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STDEV = (0.229, 0.224, 0.225)


_pil_interpolation_map = {
     "bicubic" : Image.Resampling.BICUBIC,
    "bilinear" : Image.Resampling.BILINEAR,
     "lanczos" : Image.Resampling.LANCZOS,
     "nearest" : Image.Resampling.NEAREST,
         "box" : Image.Resampling.BOX,
     "hamming" : Image.Resampling.HAMMING,
}

@dataclass
class PreprocessingParams:
    input_height: int
    input_width: int
    normalisation_mean: Optional[List[float]]
    normalisation_stdev: Optional[List[float]]
    interpolation: str
    output_format: Literal["BGR", "RGB"]
    resize_method: Literal["squish", "pad"]
    pad_fill: Optional[Tuple[int, int, int]] = None

    @staticmethod
    def _check_stats_in_0_to_1_range(stats: Tuple[float, float, float]):
        for x in stats:
            if x > 1.0:
                raise RuntimeError(f"Normalisation stats should be between 0-1. Got {stats}")

    @property
    def pil_interpolation_method(self) -> Image.Resampling:
        return _pil_interpolation_map[self.interpolation]

    def __post_init__(self):
        if self.normalisation_mean is not None:  self._check_stats_in_0_to_1_range(self.normalisation_mean)
        if self.normalisation_stdev is not None: self._check_stats_in_0_to_1_range(self.normalisation_stdev)
        if not self.output_format in ("BGR", "RGB"):          raise ValueError
        if not self.interpolation in _pil_interpolation_map.keys():
            raise ValueError(
                f"resize method '{self.interpolation}' is invalid. Valid choices are: {list(_pil_interpolation_map.keys())}"
            )

    def create_coreml_input(self, input_name: str = "Image") -> List['ct.ImageType']:
        from upyog.ml.coreml_utils import get_coreml_input

        return get_coreml_input(
            H = self.input_height,
            W = self.input_width,
            norm_mean = self.normalisation_mean,
            norm_stdev = self.normalisation_stdev,
            input_name = input_name,
            input_format = self.output_format,
        )