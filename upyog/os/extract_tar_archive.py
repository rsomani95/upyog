import shutil
import tarfile
import tempfile

from copy import deepcopy
from collections import defaultdict
from pathlib import Path
from tqdm import tqdm
from rich import print
from upyog.cli import call_parse, P
from upyog.os import get_files, load_json


@call_parse
def extract_and_organize_tarfiles(
    root_dir: P("Path to the root directory with the `.tar` files"),
    output_dir: P("(Optional) Path to the output dir. If not provided, outputs are saved in `root_dir`") = None,
    extract_structure: P("(Optional) Path to a JSON file that captures the output structure. If not provided, we attempt to detect it automatically") = None,
):
    """
    ----- extract-and-organise-tar-archive -----

    This program extracts and organizes files from .tar archives. It was originally designed to be
    used with the DataComp dataset, where each tar file has a group of files per 'base' file.

    The `extract_structure` can be provided beforehand via a JSON file like this:
    {
        ".json": "json_data",
        ".txt": "caption",
        ".url.txt": "url"
    }

    If not provided, it is automatically detected.
    Then, we extract all the files, and create subfolders for each type in the structure.
    """
    root_dir = Path(root_dir)
    output_dir = Path(output_dir) if output_dir else root_dir

    if extract_structure:
        extract_structure = load_json(extract_structure)

    print("Starting extraction and organization process...")

    tar_files = get_files(root_dir, extensions=[".tar"])
    tar_files.sort()
    total_files = len(tar_files)
    print(f"Found {total_files} .tar files to process.")

    # Detect structure using the first .tar file
    if extract_structure is None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with tarfile.open(tar_files[0], "r") as tar:
                tar.extractall(temp_dir)
            temp_path = Path(temp_dir)
            extract_structure = detect_structure(temp_path)
        print(f"Detected structure:\n{extract_structure}")

    # Create directories based on the extract structure
    for subdir in extract_structure.values():
        output_dir.joinpath(subdir).mkdir(parents=True, exist_ok=True)

    # Loop through all .tar files
    progress_bar = tqdm(tar_files, "Extracting .tar files", unit="file")
    for tar_file in progress_bar:
        progress_bar.set_description(f"Extracting {tar_file.name}")

        with tempfile.TemporaryDirectory() as temp_dir:
            with tarfile.open(tar_file, "r") as tar:
                tar.extractall(temp_dir)
            temp_path = Path(temp_dir)

            for file_path in temp_path.iterdir():
                if file_path.is_file():
                    suffix = "".join(file_path.suffixes)

                    if suffix in extract_structure:
                        subdir = extract_structure[suffix]
                        shutil.move(str(file_path), str(output_dir.joinpath(subdir, file_path.name)))
                    else:
                        print(f"Warning: Unexpected suffix '{suffix}' found in file '{file_path.name}'")

    print("\n\n  Extraction and organization complete.")
    print("-----------------------------------------")
    print(f"Total .tar files processed: {len(tar_files)}")
    for subdir in extract_structure.values():
        print(f"Total {subdir} files: {len(list(output_dir.joinpath(subdir).glob('*')))}")


def detect_structure(temp_path: Path) -> dict:
    files = get_files(temp_path)
    unique_file_extensions = set(["".join(f.suffixes) for f in files])
    unique_file_extensions = sorted(unique_file_extensions)

    extract_structure = {}
    for ext in unique_file_extensions:
        assert ext.startswith(".")

        orig_ext = deepcopy(ext)

        ext = ext[1:]
        ext = ext.replace(".", "_")
        ext = ext + "__data"

        extract_structure[orig_ext] = ext

    return extract_structure
