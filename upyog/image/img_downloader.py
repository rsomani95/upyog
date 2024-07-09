import concurrent.futures
import os
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from typing import Tuple, Union

import pandas as pd
import requests
from PIL import Image
from tqdm import tqdm
from upyog.cli import call_parse, P


PathLike = Union[str, Path]


def download_image(
    url_file: PathLike,
    output_path: PathLike,
) -> Tuple[PathLike, bool, Union[str, None]]:
    """
    Download an image from a URL and save it to the output path.

    Args:
        url_file: Path to the file containing the image URL.
        output_path: Path to the output directory.

    Returns:
        A tuple containing the URL file path, success status, and error reason (if any).
    """
    try:
        with open(url_file, "r") as file:
            url = file.read().strip()

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        image_data = response.content
        try:
            Image.open(BytesIO(image_data)).verify()
        except:
            return url_file, False, "Invalid image data"

        file_name = (
            output_path / url_file.with_suffix(Path(urlparse(url).path).suffix).name
        )
        with open(file_name, "wb") as file:
            file.write(image_data)

        return url_file, True, None
    except requests.exceptions.RequestException as e:
        return url_file, False, str(e)
    except Exception as e:
        return url_file, False, str(e)


@call_parse
def download_images(
    folder_path: P("Input folder with url .txt files") = None,  # type: ignore
    output_path: P("Output folder") = None,  # type: ignore
    max_threads: P("Max. no. of threads") = os.cpu_count(),  # type: ignore
):
    """
    Download images from URL files in a folder using multi-threading.

    Args:
        folder_path: Path to the input folder containing URL files.
        output_path: Path to the output folder for saving downloaded images.
        max_threads: Maximum number of threads to use for downloading.
    """
    assert folder_path
    assert output_path

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
                url_file, success, reason = future.result()
                progress.update(1)
                progress.set_postfix_str(
                    f"{progress.n}/{total_files} ({progress.n / total_files * 100:.2f}%)"
                )
                results.append(
                    {"url_file": str(url_file), "success": success, "reason": reason}
                )

    df = pd.DataFrame(results)
    success_count = df["success"].sum()
    success_rate = success_count / total_files * 100
    print(
        f"\nDownloaded {success_count} out of {total_files} images ({success_rate:.2f}% success rate)"
    )

    output_file = output_path / "download_results.csv"
    df.to_csv(output_file, index=False)
    print(f"\nDownload results saved to: {output_file}")
