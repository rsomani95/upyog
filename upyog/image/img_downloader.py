import concurrent.futures
import os

from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from typing import Union
from urllib.parse import urlparse


import pandas as pd
import requests

from PIL import Image
from tqdm import tqdm
from upyog.cli import P, call_parse

PathLike = Union[str, Path]


@dataclass
class DownloadResult:
    url_file: PathLike
    success: bool
    reason: Union[str, None]


def download_image(
    url_file: PathLike,
    output_path: PathLike,
    convert_rgb: bool = True,
) -> DownloadResult:
    """
    Download an image from a URL and save it to the output path.

    Args:
        url_file: Path to the file containing the image URL.
        output_path: Path to the output directory.

    Returns:
        A DownloadResult object containing the URL file path, success status, and error reason (if any).
    """
    try:
        with open(url_file, "r") as file:
            url = file.read().strip()

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        image_data = response.content
        try:
            image = Image.open(BytesIO(image_data))
            # NOTE: Calling `.verify()` invalidates the image and needs it to be
            # re-loaded. We'll end up catching this error on `.save()` instead
            # image.verify()  

        except:
            return DownloadResult(url_file, False, "Invalid image data")

        try:
            if convert_rgb:
                image = image.convert("RGB")
                extension = "jpg"

            else:
                extension = image.format.lower()
                if extension in ["jpeg", ""]:
                    extension = "jpg"

            file_name = output_path / f"{url_file.stem.replace('.url', '')}.{extension}"
            image.save(file_name)

        except Exception as e:
            return DownloadResult(url_file, False, str(e))

        return DownloadResult(url_file, True, None)

    except requests.exceptions.RequestException as e:
        return DownloadResult(url_file, False, str(e))

    except Exception as e:
        return DownloadResult(url_file, False, str(e))


@call_parse
def download_images(
    i: P("Input folder with url .txt files") = None,  # type: ignore
    o: P("Output folder") = None,  # type: ignore
    max_threads: P("Max. no. of threads") = os.cpu_count(),  # type: ignore
):
    """
    Download images from URL files in a folder using multi-threading.

    Args:
        folder_path: Path to the input folder containing URL files.
        output_path: Path to the output folder for saving downloaded images.
        max_threads: Maximum number of threads to use for downloading.
    """
    assert i
    assert o

    folder_path = i
    output_path = o

    url_files = list(Path(folder_path).glob("*.url.txt"))
    total_files = len(url_files)

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [
            executor.submit(download_image, url_file, output_path)
            for url_file in url_files
        ]

        with tqdm(
            total=total_files, unit="file", desc="Downloading images"
        ) as progress:
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                progress.update(1)
                progress.set_postfix_str(
                    f"{progress.n}/{total_files} ({progress.n / total_files * 100:.2f}%)"
                )
                results.append(result)

    df = pd.DataFrame([asdict(result) for result in results])
    success_count = df["success"].sum()
    success_rate = success_count / total_files * 100
    print(
        f"\nDownloaded {success_count} out of {total_files} images ({success_rate:.2f}% success rate)"
    )

    output_file = output_path / "download_results.csv"
    df.to_csv(output_file, index=False)
    print(f"\nDownload results saved to: {output_file}")
