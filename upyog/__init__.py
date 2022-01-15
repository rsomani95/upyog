from upyog.imports import *


install()
logger.opt(colors=True)
tqdm.pandas()
ImageFile.LOAD_TRUNCATED_IMAGES = True


pil_version = PIL.__version__

if not "post" in pil_version:
    msg = f"Pillow-SIMD not installed. Using PIL {pil_version} instead"
    warnings.warn(msg)

else:
    if not PILFeatures.check_feature("libjpeg_turbo"):
        warnings.warn(
            f"Pillow-SIMD is installed, but Libjpeg Turbo is not being used. "
            f"Unlikely to see any speedups"
        )
