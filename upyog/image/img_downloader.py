import concurrent.futures
import os
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
from PIL import Image
from rich.progress import Progress
from rich import print
from upyog.cli import call_parse, P
from typing import Union


def download_image(url_file: Union[str, Path], output_path: Path):
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
    output_path: P("Output folder") = None,# type: ignore
    max_threads: P("Max. no. of threads") = os.cpu_count(),# type: ignore
):
    assert folder_path
    assert output_path

    url_files = list(Path(folder_path).glob("*.url.txt"))
    total_files = len(url_files)

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []
    with Progress() as progress:
        download_task = progress.add_task(
            "[green]Downloading images...", total=total_files
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [
                executor.submit(download_image, url_file, output_path)
                for url_file in url_files
            ]

            for future in concurrent.futures.as_completed(futures):
                url_file, success, reason = future.result()
                progress.update(download_task, advance=1)
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
